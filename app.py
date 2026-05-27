from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import locale
import os
import requests
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mi_secreto_super_seguro_para_mvp')  # Necesario para sesiones y flash messages
# Usar base de datos externa en producción (ej. Postgres) y SQLite en local
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mundial.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['UPLOAD_FOLDER'] = 'static/uploads/perfiles'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# ==========================================
# CONFIGURACIÓN DEL SCHEDULER (ACTUALIZACIONES AUTOMÁTICAS)
# ==========================================
IS_VERCEL = os.environ.get('VERCEL') == '1'

scheduler = BackgroundScheduler()
if not IS_VERCEL:
    scheduler.start()

# ==========================================
# 0. ARQUITECTURA DE DATOS (DATA-DRIVEN)
# ==========================================
MUNDIAL_DATA = {
    'Grupos': {
        'A': [
            {'nombre': 'México', 'code': 'mx', 'pj': 0, 'pts': 0},
            {'nombre': 'Sudáfrica', 'code': 'za', 'pj': 0, 'pts': 0},
            {'nombre': 'Corea del Sur', 'code': 'kr', 'pj': 0, 'pts': 0},
            {'nombre': 'Chequia', 'code': 'cz', 'pj': 0, 'pts': 0}
        ],
        'B': [
            {'nombre': 'Canadá', 'code': 'ca', 'pj': 0, 'pts': 0},
            {'nombre': 'Bosnia y Herzegovina', 'code': 'ba', 'pj': 0, 'pts': 0},
            {'nombre': 'Catar', 'code': 'qa', 'pj': 0, 'pts': 0},
            {'nombre': 'Suiza', 'code': 'ch', 'pj': 0, 'pts': 0}
        ],
        'C': [
            {'nombre': 'Brasil', 'code': 'br', 'pj': 0, 'pts': 0},
            {'nombre': 'Marruecos', 'code': 'ma', 'pj': 0, 'pts': 0},
            {'nombre': 'Haití', 'code': 'ht', 'pj': 0, 'pts': 0},
            {'nombre': 'Escocia', 'code': 'gb-sct', 'pj': 0, 'pts': 0}
        ],
        'D': [
            {'nombre': 'Estados Unidos', 'code': 'us', 'pj': 0, 'pts': 0},
            {'nombre': 'Paraguay', 'code': 'py', 'pj': 0, 'pts': 0},
            {'nombre': 'Australia', 'code': 'au', 'pj': 0, 'pts': 0},
            {'nombre': 'Turquía', 'code': 'tr', 'pj': 0, 'pts': 0}
        ],
        'E': [
            {'nombre': 'Alemania', 'code': 'de', 'pj': 0, 'pts': 0},
            {'nombre': 'Ecuador', 'code': 'ec', 'pj': 0, 'pts': 0},
            {'nombre': 'Costa de Marfil', 'code': 'ci', 'pj': 0, 'pts': 0},
            {'nombre': 'Curazao', 'code': 'cw', 'pj': 0, 'pts': 0}
        ],
        'F': [
            {'nombre': 'Países Bajos', 'code': 'nl', 'pj': 0, 'pts': 0},
            {'nombre': 'Japón', 'code': 'jp', 'pj': 0, 'pts': 0},
            {'nombre': 'Suecia', 'code': 'se', 'pj': 0, 'pts': 0},
            {'nombre': 'Túnez', 'code': 'tn', 'pj': 0, 'pts': 0}
        ],
        'G': [
            {'nombre': 'Bélgica', 'code': 'be', 'pj': 0, 'pts': 0},
            {'nombre': 'Egipto', 'code': 'eg', 'pj': 0, 'pts': 0},
            {'nombre': 'Irán', 'code': 'ir', 'pj': 0, 'pts': 0},
            {'nombre': 'Nueva Zelanda', 'code': 'nz', 'pj': 0, 'pts': 0}
        ],
        'H': [
            {'nombre': 'España', 'code': 'es', 'pj': 0, 'pts': 0},
            {'nombre': 'Cabo Verde', 'code': 'cv', 'pj': 0, 'pts': 0},
            {'nombre': 'Arabia Saudita', 'code': 'sa', 'pj': 0, 'pts': 0},
            {'nombre': 'Uruguay', 'code': 'uy', 'pj': 0, 'pts': 0}
        ],
        'I': [
            {'nombre': 'Francia', 'code': 'fr', 'pj': 0, 'pts': 0},
            {'nombre': 'Senegal', 'code': 'sn', 'pj': 0, 'pts': 0},
            {'nombre': 'Irak', 'code': 'iq', 'pj': 0, 'pts': 0},
            {'nombre': 'Noruega', 'code': 'no', 'pj': 0, 'pts': 0}
        ],
        'J': [
            {'nombre': 'Argentina', 'code': 'ar', 'pj': 0, 'pts': 0},
            {'nombre': 'Argelia', 'code': 'dz', 'pj': 0, 'pts': 0},
            {'nombre': 'Austria', 'code': 'at', 'pj': 0, 'pts': 0},
            {'nombre': 'Jordania', 'code': 'jo', 'pj': 0, 'pts': 0}
        ],
        'K': [
            {'nombre': 'Portugal', 'code': 'pt', 'pj': 0, 'pts': 0},
            {'nombre': 'RD Congo', 'code': 'cd', 'pj': 0, 'pts': 0},
            {'nombre': 'Uzbekistán', 'code': 'uz', 'pj': 0, 'pts': 0},
            {'nombre': 'Colombia', 'code': 'co', 'pj': 0, 'pts': 0}
        ],
        'L': [
            {'nombre': 'Inglaterra', 'code': 'gb-eng', 'pj': 0, 'pts': 0},
            {'nombre': 'Croacia', 'code': 'hr', 'pj': 0, 'pts': 0},
            {'nombre': 'Ghana', 'code': 'gh', 'pj': 0, 'pts': 0},
            {'nombre': 'Panamá', 'code': 'pa', 'pj': 0, 'pts': 0}
        ]
    }
}

# ==========================================
# 1. MODELOS DE BASE DE DATOS
# ==========================================

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    foto_perfil = db.Column(db.String(255), nullable=True, default='img/default_perfil.png')
    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable para compatibilidad con usuarios previos
    # Relación inversa para saber qué predicciones y votos hizo un usuario
    votos = db.relationship('Voto', backref='usuario', lazy=True)

    def __init__(self, nombre=None, email=None, foto_perfil='img/default_perfil.png', is_admin=False, **kwargs):
        self.nombre = nombre
        self.email = email
        self.foto_perfil = foto_perfil
        self.is_admin = is_admin
        super(Usuario, self).__init__(**kwargs)

    def set_password(self, password):
        """Hashea y almacena la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipo_a = db.Column(db.String(50), nullable=False)
    equipo_b = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    grupo = db.Column(db.String(10), nullable=True) # ej: 'A', 'B'
    fase = db.Column(db.String(50), nullable=False) # ej: 'Fase de Grupos'
    
    # ACTUALIZACIONES EN TIEMPO REAL
    goles_a = db.Column(db.Integer, nullable=True, default=0)
    goles_b = db.Column(db.Integer, nullable=True, default=0)
    estado = db.Column(db.String(20), nullable=True, default='scheduled')
    
    # RESULTADOS DE TARJETAS (NUEVO)
    amarilla_real = db.Column(db.String(1), nullable=True) # 'A' o 'B'
    roja_real = db.Column(db.String(1), nullable=True)     # 'A' o 'B'

    def __init__(self, equipo_a=None, equipo_b=None, fecha=None, grupo=None, fase=None, goles_a=0, goles_b=0, estado='scheduled', amarilla_real=None, roja_real=None, **kwargs):
        self.equipo_a = equipo_a
        self.equipo_b = equipo_b
        self.fecha = fecha
        self.grupo = grupo
        self.fase = fase
        self.goles_a = goles_a
        self.goles_b = goles_b
        self.estado = estado
        self.amarilla_real = amarilla_real
        self.roja_real = roja_real
        super(Partido, self).__init__(**kwargs)


class Voto(db.Model):
    """Modelo de votación única por partido. Almacena predicción de ganador y tarjetas."""
    id = db.Column(db.Integer, primary_key=True)
    voto_ganador = db.Column(db.String(1), nullable=False)    # 'A' o 'B'
    voto_amarilla = db.Column(db.String(1), nullable=False)   # 'A' o 'B'
    voto_roja = db.Column(db.String(1), nullable=False)       # 'A' o 'B'
    
    # Nuevos campos para resultado exacto y desempate
    goles_a_prediccion = db.Column(db.Integer, nullable=True) # Permitimos null para compatibilidad previa
    goles_b_prediccion = db.Column(db.Integer, nullable=True)
    fecha_voto = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)
    
    # Relación para acceder a los datos del partido desde el voto
    partido = db.relationship('Partido', backref=db.backref('votos_rel', lazy=True))

    def __init__(self, voto_ganador=None, voto_amarilla=None, voto_roja=None, goles_a_prediccion=None, goles_b_prediccion=None, fecha_voto=None, usuario_id=None, partido_id=None, **kwargs):
        self.voto_ganador = voto_ganador
        self.voto_amarilla = voto_amarilla
        self.voto_roja = voto_roja
        self.goles_a_prediccion = goles_a_prediccion
        self.goles_b_prediccion = goles_b_prediccion
        if fecha_voto is not None:
            self.fecha_voto = fecha_voto
        self.usuario_id = usuario_id
        self.partido_id = partido_id
        super(Voto, self).__init__(**kwargs)

    # Restricción: un usuario solo puede votar una vez por partido
    __table_args__ = (db.UniqueConstraint('usuario_id', 'partido_id', name='unique_voto_por_partido'),)


# ==========================================
# 2. PROCESADOR DE CONTEXTO (PARA UI)
# ==========================================
@app.context_processor
def inject_user_and_date():
    """Inyecta el usuario actual y la fecha en todas las plantillas."""
    usuario_actual = None
    if 'usuario_id' in session:
        usuario_actual = Usuario.query.get(session['usuario_id'])
    
    # Intentar poner fecha en español si es posible, si no, default
    try:
        # locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') # Puede fallar en Windows sin el pack de idioma
        ahora = datetime.now().strftime("%d-%m-%Y %H:%M")
    except:
        ahora = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    # Mapeo de banderas consolidado en MUNDIAL_DATA para evitar redundancia
    # Extraemos country_codes de la estructura central
    country_codes = {}
    for grupo_id, equipos in MUNDIAL_DATA['Grupos'].items():
        for eq in equipos:
            country_codes[eq['nombre']] = eq['code']
        
    return dict(usuario_actual=usuario_actual, fecha_actual=ahora, country_codes=country_codes, MUNDIAL_DATA=MUNDIAL_DATA)

# ==========================================
# 3. DECORADORES Y UTILIDADES DE SEGURIDAD
# ==========================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder al panel de administración.', 'error')
            return redirect(url_for('login', next=request.url))
        
        usuario_actual = Usuario.query.get(session['usuario_id'])
        if not usuario_actual or not usuario_actual.is_admin:
            flash('Acceso denegado. No tienes permisos de administrador.', 'error')
            return redirect(url_for('inicio'))
            
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# 4. RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(password):
            session.permanent = True
            session['usuario_id'] = usuario.id
            flash(f'Bienvenido de nuevo, {usuario.nombre}!', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Correo o contraseña incorrectos.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('inicio'))

# ==========================================
# 4. RUTAS PRINCIPALES
# ==========================================

def _calcular_porcentajes(partido_id):
    votos = Voto.query.filter_by(partido_id=partido_id).all()
    total = len(votos)
    if total == 0:
        return {'total': 0, 'ganador': {'A': 50, 'B': 50, 'E': 0}}
    
    g_a = sum(1 for v in votos if v.voto_ganador == 'A')
    g_b = sum(1 for v in votos if v.voto_ganador == 'B')
    g_e = sum(1 for v in votos if v.voto_ganador == 'E')
    
    return {
        'total': total,
        'ganador': {
            'A': round((g_a / total) * 100), 
            'B': round((g_b / total) * 100),
            'E': round((g_e / total) * 100)
        }
    }

@app.route('/')
def inicio():
    """Página de inicio que lista los partidos del Mundial con stats."""
    partidos_db = Partido.query.all()
    partidos_json = []
    for p in partidos_db:
        # Puntos 3 y 4: Añadimos metrics y stats precalculados para el Frontend
        stats = _calcular_porcentajes(p.id)
        partidos_json.append({
            'id': p.id,
            'equipo_a': p.equipo_a,
            'equipo_b': p.equipo_b,
            'fecha': p.fecha.isoformat(),
            'grupo': p.grupo,
            'fase': p.fase,
            'estado': p.estado,
            'goles_a': p.goles_a,
            'goles_b': p.goles_b,
            'amarilla_real': p.amarilla_real,
            'roja_real': p.roja_real,
            'stats': stats
        })
    return render_template('index.html', partidos=partidos_json)

@app.route('/grupos')
def grupos():
    """Muestra las tablas de posiciones de los grupos."""
    return render_template('grupos.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Ruta básica para registrar usuarios."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        if not password or len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres.', 'error')
            return redirect(url_for('registro'))
        
        # Validar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Este correo electrónico ya está registrado.', 'error')
            return redirect(url_for('registro'))
            
        # Crear, hashear contraseña y guardar nuevo usuario
        nuevo_usuario = Usuario(nombre=nombre, email=email)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso. ¡Empieza a hacer tus predicciones!', 'success')
        return redirect(url_for('inicio'))
        
    return render_template('registro.html')

@app.route('/apostar/<int:id_partido>')
def apostar(id_partido):
    """Muestra la pantalla de votación o resultados según si el usuario ya votó."""
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para hacer una apuesta.', 'warning')
        return redirect(url_for('login'))

    partido = Partido.query.get_or_404(id_partido)
    usuario_id = session['usuario_id']
    
    # Verificar si el usuario ya votó en este partido
    voto_existente = Voto.query.filter_by(usuario_id=usuario_id, partido_id=id_partido).first()
    ya_voto = voto_existente is not None
    
    # Datos del partido como diccionario para el frontend JS
    partido_data = {
        'id': partido.id,
        'equipo_a': partido.equipo_a,
        'equipo_b': partido.equipo_b,
        'fecha': partido.fecha.strftime('%d/%m/%Y %H:%M'),
        'grupo': partido.grupo,
        'fase': partido.fase
    }
    
    return render_template('apostar.html', partido=partido, partido_data=partido_data, ya_voto=ya_voto)


@app.route('/perfil')
def perfil():
    """Muestra el historial de predicciones/votos del usuario activo."""
    if 'usuario_id' not in session:
        flash('Inicia sesión para ver tu perfil.', 'warning')
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['usuario_id'])
    votos = Voto.query.filter_by(usuario_id=usuario.id).all()
    
    # Preparar datos más fáciles de consumir para la plantilla
    historial = []
    for voto in votos:
        historial.append({
            'partido': voto.partido,
            'voto_ganador': voto.voto_ganador,
            'voto_amarilla': voto.voto_amarilla,
            'voto_roja': voto.voto_roja
        })
        
    return render_template('perfil.html', usuario=usuario, historial=historial)

@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    """Permite al usuario actualizar su foto de perfil mediante subida de archivo o URL."""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    usuario = Usuario.query.get(session['usuario_id'])
    
    # 1. Intentar procesar subida de archivo
    if 'foto' in request.files:
        file = request.files['foto']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(f"user_{usuario.id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Asegurar que el directorio existe
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)
            
            # Guardamos la ruta relativa para usarla con url_for('static', filename=...)
            usuario.foto_perfil = f"uploads/perfiles/{filename}"
            db.session.commit()
            flash('¡Foto de perfil subida con éxito!', 'success')
            return redirect(url_for('perfil'))

    # 2. Si no hay archivo, intentar procesar URL
    nueva_foto_url = request.form.get('foto_url')
    
    if nueva_foto_url:
        usuario.foto_perfil = nueva_foto_url
        db.session.commit()
        flash('Foto de perfil actualizada mediante URL.', 'success')
    else:
        # Caso de restablecimiento (botón Quitar o vacío)
        usuario.foto_perfil = 'img/default_perfil.png'
        db.session.commit()
        flash('Se ha restablecido la foto por defecto.', 'info')
        
    return redirect(url_for('perfil'))

@app.route('/mis_predicciones')
def mis_predicciones():
    """Muestra el resumen de porcentajes de todos los partidos."""
    partidos = Partido.query.order_by(Partido.fecha).all()
    resumen_partidos = []
    
    for p in partidos:
        porcentajes = _calcular_porcentajes(p.id)
        resumen_partidos.append({
            'info': p,
            'stats': porcentajes
        })
        
    return render_template('mis_predicciones.html', resumen=resumen_partidos)

# ==========================================
# 5. API REST (AJAX)
# ==========================================

def _calcular_porcentajes(partido_id):
    """Calcula los porcentajes de votos para un partido dado."""
    votos = Voto.query.filter_by(partido_id=partido_id).all()
    total = len(votos)
    if total == 0:
        return {'total': 0, 'ganador': {'A': 50, 'B': 50, 'E': 0}, 'amarilla': {'A': 50, 'B': 50}, 'roja': {'A': 50, 'B': 50}}
    
    g_a = sum(1 for v in votos if v.voto_ganador == 'A')
    g_b = sum(1 for v in votos if v.voto_ganador == 'B')
    g_e = sum(1 for v in votos if v.voto_ganador == 'E')
    
    am_a = sum(1 for v in votos if v.voto_amarilla == 'A')
    ro_a = sum(1 for v in votos if v.voto_roja == 'A')
    
    return {
        'total': total,
        'ganador': {
            'A': round((g_a / total) * 100), 
            'B': round((g_b / total) * 100),
            'E': round((g_e / total) * 100)
        },
        'amarilla': {'A': round((am_a / total) * 100), 'B': round(((total - am_a) / total) * 100)},
        'roja': {'A': round((ro_a / total) * 100), 'B': round(((total - ro_a) / total) * 100)}
    }

@app.route('/api/votar/<int:id_partido>', methods=['POST'])
def api_votar(id_partido):
    """Recibe el voto del usuario via AJAX y retorna los porcentajes actualizados."""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    usuario_id = session['usuario_id']
    
    # Restricción: un usuario solo puede votar una vez por partido
    voto_existente = Voto.query.filter_by(usuario_id=usuario_id, partido_id=id_partido).first()
    if voto_existente:
        return jsonify({'error': 'Ya has votado en este partido'}), 409
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos inválidos'}), 400
    
    ganador = data.get('ganador')
    amarilla = data.get('amarilla')
    roja = data.get('roja')
    
    # Nuevos campos de resultado exacto
    goles_a = data.get('goles_a')
    goles_b = data.get('goles_b')
    
    if ganador not in ('A', 'B', 'E') or amarilla not in ('A', 'B') or roja not in ('A', 'B'):
        return jsonify({'error': 'Valores inválidos. Deben ser A o B.'}), 400
        
    try:
        goles_a = int(goles_a)
        goles_b = int(goles_b)
        if goles_a < 0 or goles_b < 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({'error': 'Goles deben ser numéricos y no negativos.'}), 400
    
    nuevo_voto = Voto(
        voto_ganador=ganador,
        voto_amarilla=amarilla,
        voto_roja=roja,
        goles_a_prediccion=goles_a,
        goles_b_prediccion=goles_b,
        fecha_voto=datetime.utcnow(),
        usuario_id=usuario_id,
        partido_id=id_partido
    )
    db.session.add(nuevo_voto)
    db.session.commit()
    
    porcentajes = _calcular_porcentajes(id_partido)
    return jsonify({
        'success': True, 
        'porcentajes': porcentajes,
        'mi_voto': {
            'ganador': ganador,
            'amarilla': amarilla,
            'roja': roja,
            'goles_a': goles_a,
            'goles_b': goles_b
        }
    })

@app.route('/api/resultados/<int:id_partido>')
def api_resultados(id_partido):
    """Retorna los porcentajes de votos actuales y el voto del usuario actual si existe."""
    Partido.query.get_or_404(id_partido)
    porcentajes = _calcular_porcentajes(id_partido)
    
    mi_voto = None
    if 'usuario_id' in session:
        voto_existente = Voto.query.filter_by(usuario_id=session['usuario_id'], partido_id=id_partido).first()
        if voto_existente:
            mi_voto = {
                'ganador': voto_existente.voto_ganador,
                'amarilla': voto_existente.voto_amarilla,
                'roja': voto_existente.voto_roja,
                'goles_a': voto_existente.goles_a_prediccion,
                'goles_b': voto_existente.goles_b_prediccion
            }
            
    return jsonify({
        'porcentajes': porcentajes,
        'mi_voto': mi_voto
    })


# ==========================================
# 6. RANKING GLOBAL
# ==========================================

@app.route('/ranking')
def ranking():
    """Calcula y muestra el ranking global de usuarios basado en sus predicciones."""
    usuarios = Usuario.query.all()
    partidos_finalizados = Partido.query.filter_by(estado='finished').all()
    
    # Crear lookup rápido de resultados reales de los partidos finalizados
    resultados = {}
    for p in partidos_finalizados:
        ganador_real = 'E' # Empate por defecto
        
        if p.goles_a is not None and p.goles_b is not None:
            if p.goles_a > p.goles_b:
                ganador_real = 'A'
            elif p.goles_b > p.goles_a:
                ganador_real = 'B'
                
        resultados[p.id] = {
            'ganador_real': ganador_real,
            'goles_a': p.goles_a,
            'goles_b': p.goles_b,
            'amarilla_real': p.amarilla_real,
            'roja_real': p.roja_real
        }
        
    ranking_data = []
    
    for u in usuarios:
        puntos_totales = 0
        votos_usuario = Voto.query.filter_by(usuario_id=u.id).all()
        
        for v in votos_usuario:
            if v.partido_id in resultados:
                res = resultados[v.partido_id]
                
                # 1. Acierto de Ganador/Empate (3 pts)
                if v.voto_ganador == res['ganador_real']:
                    puntos_totales += 3
                    
                # 2. Marcador Exacto (+5 pts adicionales)
                if res['goles_a'] is not None and res['goles_b'] is not None:
                    if v.goles_a_prediccion == res['goles_a'] and v.goles_b_prediccion == res['goles_b']:
                        puntos_totales += 5
                        
                # 3. Primera Amarilla correcta (2 pts)
                if res['amarilla_real'] is not None and v.voto_amarilla == res['amarilla_real']:
                    puntos_totales += 2
                    
                # 4. Primera Roja correcta (7 pts)
                if res['roja_real'] is not None and v.voto_roja == res['roja_real']:
                    puntos_totales += 7
                    
        ranking_data.append({
            'usuario': u,
            'puntos': puntos_totales
        })
        
    # Ordenar por puntos totales descendente
    ranking_data.sort(key=lambda x: x['puntos'], reverse=True)
    
    # Asignar posición resolviendo empates simples (opcional mejora pero al menos tener índice)
    for index, data in enumerate(ranking_data):
        data['posicion'] = index + 1
    
    return render_template('ranking.html', ranking_data=ranking_data)

# ==========================================
# 6.5 PANEL DE ADMINISTRACIÓN
# ==========================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_usuarios = Usuario.query.count()
    total_partidos = Partido.query.count()
    partidos_en_vivo = Partido.query.filter_by(estado='live').count()
    total_votos = Voto.query.count()
    
    return render_template('admin/dashboard.html', 
                           total_usuarios=total_usuarios, 
                           total_partidos=total_partidos,
                           partidos_en_vivo=partidos_en_vivo,
                           total_votos=total_votos)

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/partidos', methods=['GET', 'POST'])
@admin_required
def admin_partidos():
    if request.method == 'POST':
        # Simple handler to override a match manually
        partido_id = request.form.get('partido_id')
        goles_a = request.form.get('goles_a')
        goles_b = request.form.get('goles_b')
        estado = request.form.get('estado')
        
        p = Partido.query.get(partido_id)
        if p:
            if goles_a != '': p.goles_a = int(goles_a)
            if goles_b != '': p.goles_b = int(goles_b)
            if estado: p.estado = estado
            db.session.commit()
            flash(f'¡El partido {p.equipo_a} vs {p.equipo_b} ha sido actualizado manualmente!', 'success')
        return redirect(url_for('admin_partidos'))
        
    partidos = Partido.query.order_by(Partido.fecha).all()
    return render_template('admin/partidos.html', partidos=partidos)

@app.route('/admin/hacer_admin/<int:user_id>', methods=['POST'])
@admin_required
def hacer_admin(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    usuario.is_admin = not usuario.is_admin # Toggle
    db.session.commit()
    return redirect(url_for('admin_usuarios'))

# ==========================================
# 7. ACTUALIZACIONES EN TIEMPO REAL
# ==========================================
def actualizar_marcadores():
    """Consulta API-Football y actualiza los marcadores en la BD local."""
    with app.app_context():
        api_key = os.environ.get('API_FOOTBALL_KEY')
        if not api_key or api_key == 'tu_api_key_aqui':
            print("Esperando clave API válida en .env")
            return
            
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': api_key
        }
        
        try:
            response = requests.get('https://v3.football.api-sports.io/fixtures?live=all', headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'response' in data:
                estado_mapping = {
                    'NS': 'scheduled', 'TBD': 'scheduled',
                    '1H': 'live', '2H': 'live', 'HT': 'live', 'ET': 'live', 'P': 'live', 'LIVE': 'live',
                    'FT': 'finished', 'AET': 'finished', 'PEN': 'finished'
                }

                for fixture in data['response']:
                    home_team = fixture['teams']['home']['name']
                    away_team = fixture['teams']['away']['name']
                    goals_home = fixture['goals']['home']
                    goals_away = fixture['goals']['away']
                    status_short = fixture['fixture']['status']['short']
                    
                    nuevo_estado = estado_mapping.get(status_short, 'scheduled')
                    
                    partido = Partido.query.filter(
                        ((Partido.equipo_a == home_team) & (Partido.equipo_b == away_team)) |
                        ((Partido.equipo_a == away_team) & (Partido.equipo_b == home_team))
                    ).first()
                    
                    if partido:
                        if partido.equipo_a == home_team:
                            partido.goles_a = goals_home if goals_home is not None else partido.goles_a
                            partido.goles_b = goals_away if goals_away is not None else partido.goles_b
                        else:
                            partido.goles_a = goals_away if goals_away is not None else partido.goles_a
                            partido.goles_b = goals_home if goals_home is not None else partido.goles_b
                        
                        partido.estado = nuevo_estado
                
                db.session.commit()
                print("Marcadores actualizados correctamente desde la API.")
        except Exception as e:
            print(f"Error al actualizar marcadores desde la API: {e}")

# Ejecutar actualización cada 10 minutos si no estamos en Vercel
if not IS_VERCEL:
    scheduler.add_job(func=actualizar_marcadores, trigger="interval", minutes=10, id='actualizar_marcadores_job')

@app.route('/api/updates')
def api_updates_live():
    """Devuelve un JSON con los marcadores de los partidos actuales."""
    partidos = Partido.query.all()
    updates = []
    
    for p in partidos:
        updates.append({
            'id': p.id,
            'goles_a': p.goles_a,
            'goles_b': p.goles_b,
            'estado': p.estado
        })
        
    return jsonify(updates)

# ==========================================
# 3. SEMILLA DE DATOS (PARA PRUEBAS)
# ==========================================
def poblar_datos_iniciales():
    """Crea datos iniciales en la DB para probar el MVP si está vacía."""
    # Limpiamos las tablas relacionadas a partidos para asegurar la sincronización
    try:
        Voto.query.delete()
        Partido.query.delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al limpiar datos de prueba: {e}")

    # Chequeamos el usuario mock
    if not Usuario.query.filter_by(email="prueba@mundial.com").first():
        u1 = Usuario(nombre="Usuario Prueba", email="prueba@mundial.com", is_admin=True)
        db.session.add(u1)
        
    # Generar cronograma completo de 72 partidos de fase de grupos (Ajuste oficial)
    partidos_a_insertar = []
    grupos_letras = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    
    todos_los_enfrentamientos = []
    
    for grupo_id in grupos_letras:
        equipos = MUNDIAL_DATA['Grupos'][grupo_id]
        nombres_equipos = [eq['nombre'] for eq in equipos]
        
        # 6 enfrentamientos en un grupo de 4
        enfrentamientos = [
            (0, 1), (2, 3), # Jornada 1
            (0, 2), (1, 3), # Jornada 2
            (0, 3), (1, 2)  # Jornada 3
        ]
        
        for i, (idx1, idx2) in enumerate(enfrentamientos):
            eq_a = nombres_equipos[idx1]
            eq_b = nombres_equipos[idx2]
            jornada = i // 2
            todos_los_enfrentamientos.append((jornada, grupo_id, eq_a, eq_b))
            
    # Ordenar por jornada, luego por grupo para tener una secuencia lógica de partidos
    todos_los_enfrentamientos.sort(key=lambda x: (x[0], x[1]))
    
    # Calendario de partidos por día (11 al 27 de junio de 2026) = 72 partidos
    fechas_por_dia = {
        11: 2, 12: 2, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 4, 19: 4, 20: 4, 
        21: 4, 22: 4, 23: 4, 24: 6, 25: 6, 26: 6, 27: 6
    }
    
    horas_base = [13, 16, 19, 22] # Horarios de los partidos
    
    fechas_exactas = []
    for dia, num_partidos in fechas_por_dia.items():
        # Asignar horas dependiendo de cuántos partidos hay en el día
        if num_partidos == 2:
            horas_dia = [16, 19]
        elif num_partidos == 4:
            horas_dia = [13, 16, 19, 22]
        else: # 6 partidos (última jornada, se juegan a la misma hora 2 partidos)
            horas_dia = [16, 16, 19, 19, 22, 22]
            
        for i in range(num_partidos):
            fechas_exactas.append(datetime(2026, 6, dia, horas_dia[i], 0))
            
    for idx, (jornada, grupo_id, eq_a, eq_b) in enumerate(todos_los_enfrentamientos):
        fecha_partido = fechas_exactas[idx]
        p = Partido(equipo_a=eq_a, equipo_b=eq_b, fecha=fecha_partido, fase="Fase de Grupos", grupo=grupo_id)
        partidos_a_insertar.append(p)
        
    db.session.add_all(partidos_a_insertar)
    db.session.commit()
    print("Base de datos sincronizada dinámicamente con 72 partidos de Fase de Grupos.")

if __name__ == '__main__':
    print("Iniciando aplicación...")
    # Usar application context para crear la BD antes de correr
    with app.app_context():
        print("Creando tablas si no existen...")
        db.create_all()
        print("Poblando datos si la DB está vacía...")
        poblar_datos_iniciales()
        print("DB lista.")
        
    print("Iniciando Flask server en http://0.0.0.0:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
