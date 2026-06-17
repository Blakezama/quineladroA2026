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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
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
    
    # ==========================================
    # KNOCKOUT BRACKET DATA
    # ==========================================
    knockout_partidos = Partido.query.filter(Partido.fase != 'Fase de Grupos').order_by(Partido.fecha).all()
    
    # Build bracket data organized by phase
    bracket_data = {
        'Dieciseisavos de Final': [],
        'Octavos de Final': [],
        'Cuartos de Final': [],
        'Semifinales': [],
        'Final': []
    }
    
    # Get user votes for knockout matches
    usuario_actual_id = session.get('usuario_id')
    user_knockout_votes = {}
    
    for kp in knockout_partidos:
        fase_key = kp.fase
        if fase_key in bracket_data:
            match_info = {
                'id': kp.id,
                'equipo_a': kp.equipo_a,
                'equipo_b': kp.equipo_b,
                'goles_a': kp.goles_a,
                'goles_b': kp.goles_b,
                'estado': kp.estado,
                'fecha': kp.fecha.isoformat() if kp.fecha else '',
            }
            bracket_data[fase_key].append(match_info)
            
            # Get user's vote for this match
            if usuario_actual_id:
                voto = Voto.query.filter_by(usuario_id=usuario_actual_id, partido_id=kp.id).first()
                if voto:
                    user_knockout_votes[kp.id] = voto.voto_ganador  # 'A' or 'B'
    
    return render_template('index.html', partidos=partidos_json, bracket_data=bracket_data, user_knockout_votes=user_knockout_votes)

@app.route('/grupos')
def grupos():
    """Muestra las tablas de posiciones de los grupos."""
    return render_template('grupos.html')



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
    
    # Bloqueo automático: 30 minutos antes del inicio, o si el partido está en vivo o finalizado
    ahora = datetime.utcnow() - timedelta(hours=4)
    hora_limite = partido.fecha - timedelta(minutes=30)
    por_tiempo = ahora >= hora_limite
    por_estado = partido.estado in ('live', 'finished')
    partido_bloqueado = (por_tiempo or por_estado) and not ya_voto
    
    # Datos del partido como diccionario para el frontend JS
    partido_data = {
        'id': partido.id,
        'equipo_a': partido.equipo_a,
        'equipo_b': partido.equipo_b,
        'fecha': partido.fecha.strftime('%d/%m/%Y %H:%M'),
        'grupo': partido.grupo,
        'fase': partido.fase,
        'hora_limite': hora_limite.isoformat(),
        'bloqueado': partido_bloqueado
    }
    
    partido_anterior = Partido.query.get(id_partido - 1)
    partido_siguiente = Partido.query.get(id_partido + 1)
    
    return render_template('apostar.html', partido=partido, partido_data=partido_data, ya_voto=ya_voto, partido_bloqueado=partido_bloqueado, partido_anterior=partido_anterior, partido_siguiente=partido_siguiente)


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
            'goles_a': voto.goles_a_prediccion,
            'goles_b': voto.goles_b_prediccion
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
    
    # Bloqueo automático: 30 minutos antes del inicio, o si el partido está en vivo o finalizado
    partido = Partido.query.get_or_404(id_partido)
    ahora = datetime.utcnow() - timedelta(hours=4)
    hora_limite = partido.fecha - timedelta(minutes=30)
    if partido.estado in ('live', 'finished'):
        return jsonify({'error': '⏰ Pronóstico cerrado. El partido ya está en curso o ha finalizado.'}), 403
    if ahora >= hora_limite:
        return jsonify({'error': '⏰ Pronóstico cerrado. Las predicciones se bloquean 30 minutos antes del inicio del partido.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos inválidos'}), 400
    
    ganador = data.get('ganador')
    amarilla = data.get('amarilla')
    roja = data.get('roja')
    
    # Nuevos campos de resultado exacto
    goles_a = data.get('goles_a')
    goles_b = data.get('goles_b')
    
    if ganador not in ('A', 'B', 'E'):
        return jsonify({'error': 'Valores inválidos. Deben ser A o B o E.'}), 400
        
    if not amarilla:
        amarilla = 'X'
    if not roja:
        roja = 'X'
        
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
        exactos_count = 0      # Criterio desempate 1: más marcadores exactos
        diferencia_count = 0   # Criterio desempate 2: más aciertos por diferencia
        ultima_fecha_voto = None  # Criterio desempate 3: quién votó primero
        votos_usuario = Voto.query.filter_by(usuario_id=u.id).all()
        
        for v in votos_usuario:
            # Rastrear la fecha más reciente de voto del usuario
            if v.fecha_voto is not None:
                if ultima_fecha_voto is None or v.fecha_voto > ultima_fecha_voto:
                    ultima_fecha_voto = v.fecha_voto
            
            if v.partido_id in resultados:
                res = resultados[v.partido_id]
                
                # Evaluar puntuación según las reglas
                acerto_marcador = False
                acerto_ganador = (v.voto_ganador == res['ganador_real'])
                
                if res['goles_a'] is not None and res['goles_b'] is not None:
                    if v.goles_a_prediccion == res['goles_a'] and v.goles_b_prediccion == res['goles_b']:
                        acerto_marcador = True
                
                if acerto_marcador:
                    # Resultado exacto: 5 puntos
                    puntos_totales += 5
                    exactos_count += 1
                elif acerto_ganador:
                    # Diferencia: 3 puntos
                    puntos_totales += 3
                    diferencia_count += 1
                    
        ranking_data.append({
            'usuario': u,
            'puntos': puntos_totales,
            'exactos': exactos_count,
            'diferencias': diferencia_count,
            'ultima_fecha': ultima_fecha_voto
        })
        
    # Ordenar con criterios de desempate:
    # 1. Más puntos totales (descendente)
    # 2. Más marcadores exactos (descendente)
    # 3. Más aciertos por diferencia (descendente)
    # 4. Fecha de último pronóstico más temprana (ascendente = votó primero)
    ranking_data.sort(key=lambda x: (
        -x['puntos'],
        -x['exactos'],
        -x['diferencias'],
        x['ultima_fecha'] if x['ultima_fecha'] else datetime.max
    ))
    
    # Asignar posición correcta (empates reales comparten posición)
    for index, data in enumerate(ranking_data):
        if index > 0 and data['puntos'] == ranking_data[index-1]['puntos'] \
                     and data['exactos'] == ranking_data[index-1]['exactos'] \
                     and data['diferencias'] == ranking_data[index-1]['diferencias']:
            data['posicion'] = ranking_data[index-1]['posicion']
        else:
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

@app.route('/admin/partidos/<int:partido_id>/votos')
@admin_required
def admin_votos_partido(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    votos = Voto.query.filter_by(partido_id=partido_id).order_by(Voto.fecha_voto.desc()).all()
    return render_template('admin/votos_partido.html', partido=partido, votos=votos)

@app.route('/admin/hacer_admin/<int:user_id>', methods=['POST'])
@admin_required
def hacer_admin(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    usuario.is_admin = not usuario.is_admin # Toggle
    db.session.commit()
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/resetear_password/<int:user_id>', methods=['POST'])
@admin_required
def resetear_password(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    nueva_password = request.form.get('nueva_password', '').strip()
    if len(nueva_password) < 4:
        flash('La contraseña debe tener al menos 4 caracteres.', 'error')
        return redirect(url_for('admin_usuarios'))
    usuario.set_password(nueva_password)
    db.session.commit()
    flash(f'✅ Contraseña de {usuario.nombre} actualizada correctamente.', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/eliminar_usuario/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def eliminar_usuario(user_id):
    # Evitar que el admin se elimine a sí mismo si es necesario, pero como dijo "los que yo quiera", vamos a permitirlo a menos que queramos protegerlo
    if user_id == session.get('usuario_id'):
        flash('No puedes eliminar tu propio usuario.', 'error')
        return redirect(url_for('admin_usuarios'))
        
    usuario = Usuario.query.get_or_404(user_id)
    # Eliminar votos asociados primero
    Voto.query.filter_by(usuario_id=user_id).delete()
    db.session.delete(usuario)
    db.session.commit()
    flash(f'🗑️ Usuario {usuario.nombre} eliminado correctamente.', 'success')
    return redirect(url_for('admin_usuarios'))

# ==========================================
# 7. ACTUALIZACIONES EN TIEMPO REAL
# ==========================================
TRADUCCION_EQUIPOS = {
    "Mexico": "México", "South Africa": "Sudáfrica", "South Korea": "Corea del Sur",
    "Czech Republic": "Chequia", "Czechia": "Chequia", "Canada": "Canadá",
    "Bosnia and Herzegovina": "Bosnia y Herzegovina", "Qatar": "Catar",
    "Switzerland": "Suiza", "Brazil": "Brasil", "Morocco": "Marruecos",
    "Haiti": "Haití", "Scotland": "Escocia", "United States": "Estados Unidos",
    "USA": "Estados Unidos", "Paraguay": "Paraguay", "Australia": "Australia",
    "Turkey": "Turquía", "Turkiye": "Turquía", "Germany": "Alemania",
    "Ecuador": "Ecuador", "Ivory Coast": "Costa de Marfil", "Côte d'Ivoire": "Costa de Marfil",
    "Curacao": "Curazao", "Curaçao": "Curazao", "Netherlands": "Países Bajos",
    "Japan": "Japón", "Sweden": "Suecia", "Tunisia": "Túnez", "Belgium": "Bélgica",
    "Egypt": "Egipto", "Iran": "Irán", "New Zealand": "Nueva Zelanda",
    "Spain": "España", "Cape Verde": "Cabo Verde", "Saudi Arabia": "Arabia Saudita",
    "Uruguay": "Uruguay", "France": "Francia", "Senegal": "Senegal",
    "Iraq": "Irak", "Norway": "Noruega", "Argentina": "Argentina",
    "Algeria": "Argelia", "Austria": "Austria", "Jordan": "Jordania",
    "Portugal": "Portugal", "DR Congo": "RD Congo", "Congo DR": "RD Congo",
    "Uzbekistan": "Uzbekistán", "Colombia": "Colombia", "England": "Inglaterra",
    "Croatia": "Croacia", "Ghana": "Ghana", "Panama": "Panamá"
}

def actualizar_marcadores():
    """Consulta la API del Mundial 2026 (worldcup26.ir) y sincroniza los partidos."""
    with app.app_context():
        ahora = datetime.utcnow() - timedelta(hours=4)
        timestamp = ahora.strftime('%H:%M:%S')

        try:
            print(f"[{timestamp}] Consultando API Mundial 2026 (worldcup26.ir)...")
            # 1. Petición HTTP Pública a la API
            response = requests.get(
                'https://worldcup26.ir/get/games',
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            fixtures = data.get('games', [])
            print(f"  Partidos obtenidos: {len(fixtures)}")

            cambios = False
            for fixture in fixtures:
                # Extraer nombres en inglés de la API
                home_team_en = fixture.get('home_team_name_en')
                away_team_en = fixture.get('away_team_name_en')

                if not home_team_en or not away_team_en:
                    continue  # Ignorar partidos eliminatorios por definir

                # Diccionario de Traducción (Mapeo a Español)
                home_team = TRADUCCION_EQUIPOS.get(home_team_en, home_team_en)
                away_team = TRADUCCION_EQUIPOS.get(away_team_en, away_team_en)

                # Extraer marcadores
                g_h = fixture.get('home_score')
                g_a = fixture.get('away_score')
                
                try:
                    goals_home = int(g_h) if str(g_h).isdigit() else None
                    goals_away = int(g_a) if str(g_a).isdigit() else None
                except ValueError:
                    goals_home, goals_away = None, None

                # Lógica de Estados (Punto 2)
                time_elapsed = str(fixture.get('time_elapsed', '')).lower()
                finished_flag = str(fixture.get('finished', 'FALSE')).upper()

                if finished_flag == 'TRUE':
                    nuevo_estado = 'finished'
                elif time_elapsed != 'notstarted' and finished_flag == 'FALSE':
                    nuevo_estado = 'live'
                else:
                    nuevo_estado = 'scheduled'

                # Buscar en la BD Local
                partido = Partido.query.filter(
                    ((Partido.equipo_a == home_team) & (Partido.equipo_b == away_team)) |
                    ((Partido.equipo_a == away_team) & (Partido.equipo_b == home_team))
                ).first()

                if partido:
                    estado_anterior = partido.estado
                    
                    # Asignar los goles extraídos
                    if partido.equipo_a == home_team:
                        if goals_home is not None: partido.goles_a = goals_home
                        if goals_away is not None: partido.goles_b = goals_away
                    else:
                        if goals_away is not None: partido.goles_a = goals_away
                        if goals_home is not None: partido.goles_b = goals_home

                    partido.estado = nuevo_estado
                    cambios = True

                    # Imprimir solo cuando el estado cambia para evitar spam
                    if estado_anterior != nuevo_estado:
                        print(f"  [ESTADO] {partido.equipo_a} vs {partido.equipo_b}: "
                              f"{estado_anterior} -> {nuevo_estado} "
                              f"| {partido.goles_a}-{partido.goles_b}")

            if cambios:
                db.session.commit()
                print("  Sincronización de BD exitosa.")

            # 4. Resiliencia: Fallback de seguridad por si la API falla en marcar 'finished'
            partidos_sin_finalizar = Partido.query.filter(Partido.estado != 'finished').all()
            for p in partidos_sin_finalizar:
                if p.fecha + timedelta(hours=2, minutes=30) <= ahora:
                    p.estado = 'finished'
                    db.session.commit()
                    print(f"  [FALLBACK] {p.equipo_a} vs {p.equipo_b} finalizado por tiempo.")

        except Exception as e:
            # Captura general de errores de red o parsing (Punto 4)
            print(f"[{timestamp}] ERROR Crítico en la actualización API Externa: {e}")

# Ejecutar actualización cada 10 minutos si no estamos en Vercel (plan gratuito API-Football: 100 llamadas/día)
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
    if Partido.query.first():
        return

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
        
    match_schedule_2026 = [
        {'grupo': 'A', 'team1': 'México', 'team2': 'Sudáfrica', 'date': '2026-06-11', 'time_str': '13:00'},
        {'grupo': 'A', 'team1': 'Corea del Sur', 'team2': 'Chequia', 'date': '2026-06-11', 'time_str': '20:00'},
        {'grupo': 'A', 'team1': 'Chequia', 'team2': 'Sudáfrica', 'date': '2026-06-18', 'time_str': '12:00'},
        {'grupo': 'A', 'team1': 'México', 'team2': 'Corea del Sur', 'date': '2026-06-18', 'time_str': '19:00'},
        {'grupo': 'A', 'team1': 'Chequia', 'team2': 'México', 'date': '2026-06-24', 'time_str': '19:00'},
        {'grupo': 'A', 'team1': 'Sudáfrica', 'team2': 'Corea del Sur', 'date': '2026-06-24', 'time_str': '19:00'},
        {'grupo': 'B', 'team1': 'Canadá', 'team2': 'Bosnia y Herzegovina', 'date': '2026-06-12', 'time_str': '15:00'},
        {'grupo': 'B', 'team1': 'Catar', 'team2': 'Suiza', 'date': '2026-06-13', 'time_str': '12:00'},
        {'grupo': 'B', 'team1': 'Suiza', 'team2': 'Bosnia y Herzegovina', 'date': '2026-06-18', 'time_str': '12:00'},
        {'grupo': 'B', 'team1': 'Canadá', 'team2': 'Catar', 'date': '2026-06-18', 'time_str': '15:00'},
        {'grupo': 'B', 'team1': 'Suiza', 'team2': 'Canadá', 'date': '2026-06-24', 'time_str': '12:00'},
        {'grupo': 'B', 'team1': 'Bosnia y Herzegovina', 'team2': 'Catar', 'date': '2026-06-24', 'time_str': '12:00'},
        {'grupo': 'C', 'team1': 'Brasil', 'team2': 'Marruecos', 'date': '2026-06-13', 'time_str': '18:00'},
        {'grupo': 'C', 'team1': 'Haití', 'team2': 'Escocia', 'date': '2026-06-13', 'time_str': '21:00'},
        {'grupo': 'C', 'team1': 'Escocia', 'team2': 'Marruecos', 'date': '2026-06-19', 'time_str': '18:00'},
        {'grupo': 'C', 'team1': 'Brasil', 'team2': 'Haití', 'date': '2026-06-19', 'time_str': '20:30'},
        {'grupo': 'C', 'team1': 'Escocia', 'team2': 'Brasil', 'date': '2026-06-24', 'time_str': '18:00'},
        {'grupo': 'C', 'team1': 'Marruecos', 'team2': 'Haití', 'date': '2026-06-24', 'time_str': '18:00'},
        {'grupo': 'D', 'team1': 'Estados Unidos', 'team2': 'Paraguay', 'date': '2026-06-12', 'time_str': '18:00'},
        {'grupo': 'D', 'team1': 'Australia', 'team2': 'Turquía', 'date': '2026-06-13', 'time_str': '21:00'},
        {'grupo': 'D', 'team1': 'Estados Unidos', 'team2': 'Australia', 'date': '2026-06-19', 'time_str': '12:00'},
        {'grupo': 'D', 'team1': 'Turquía', 'team2': 'Paraguay', 'date': '2026-06-19', 'time_str': '20:00'},
        {'grupo': 'D', 'team1': 'Turquía', 'team2': 'Estados Unidos', 'date': '2026-06-25', 'time_str': '19:00'},
        {'grupo': 'D', 'team1': 'Paraguay', 'team2': 'Australia', 'date': '2026-06-25', 'time_str': '19:00'},
        {'grupo': 'E', 'team1': 'Alemania', 'team2': 'Curazao', 'date': '2026-06-14', 'time_str': '12:00'},
        {'grupo': 'E', 'team1': 'Costa de Marfil', 'team2': 'Ecuador', 'date': '2026-06-14', 'time_str': '19:00'},
        {'grupo': 'E', 'team1': 'Alemania', 'team2': 'Costa de Marfil', 'date': '2026-06-20', 'time_str': '16:00'},
        {'grupo': 'E', 'team1': 'Ecuador', 'team2': 'Curazao', 'date': '2026-06-20', 'time_str': '19:00'},
        {'grupo': 'E', 'team1': 'Curazao', 'team2': 'Costa de Marfil', 'date': '2026-06-25', 'time_str': '16:00'},
        {'grupo': 'E', 'team1': 'Ecuador', 'team2': 'Alemania', 'date': '2026-06-25', 'time_str': '16:00'},
        {'grupo': 'F', 'team1': 'Países Bajos', 'team2': 'Japón', 'date': '2026-06-14', 'time_str': '15:00'},
        {'grupo': 'F', 'team1': 'Suecia', 'team2': 'Túnez', 'date': '2026-06-14', 'time_str': '20:00'},
        {'grupo': 'F', 'team1': 'Países Bajos', 'team2': 'Suecia', 'date': '2026-06-20', 'time_str': '12:00'},
        {'grupo': 'F', 'team1': 'Túnez', 'team2': 'Japón', 'date': '2026-06-20', 'time_str': '22:00'},
        {'grupo': 'F', 'team1': 'Japón', 'team2': 'Suecia', 'date': '2026-06-25', 'time_str': '18:00'},
        {'grupo': 'F', 'team1': 'Túnez', 'team2': 'Países Bajos', 'date': '2026-06-25', 'time_str': '18:00'},
        {'grupo': 'G', 'team1': 'Bélgica', 'team2': 'Egipto', 'date': '2026-06-15', 'time_str': '12:00'},
        {'grupo': 'G', 'team1': 'Irán', 'team2': 'Nueva Zelanda', 'date': '2026-06-15', 'time_str': '18:00'},
        {'grupo': 'G', 'team1': 'Bélgica', 'team2': 'Irán', 'date': '2026-06-21', 'time_str': '12:00'},
        {'grupo': 'G', 'team1': 'Nueva Zelanda', 'team2': 'Egipto', 'date': '2026-06-21', 'time_str': '18:00'},
        {'grupo': 'G', 'team1': 'Egipto', 'team2': 'Irán', 'date': '2026-06-26', 'time_str': '20:00'},
        {'grupo': 'G', 'team1': 'Nueva Zelanda', 'team2': 'Bélgica', 'date': '2026-06-26', 'time_str': '20:00'},
        {'grupo': 'H', 'team1': 'España', 'team2': 'Cabo Verde', 'date': '2026-06-15', 'time_str': '12:00'},
        {'grupo': 'H', 'team1': 'Arabia Saudita', 'team2': 'Uruguay', 'date': '2026-06-15', 'time_str': '18:00'},
        {'grupo': 'H', 'team1': 'España', 'team2': 'Arabia Saudita', 'date': '2026-06-21', 'time_str': '12:00'},
        {'grupo': 'H', 'team1': 'Uruguay', 'team2': 'Cabo Verde', 'date': '2026-06-21', 'time_str': '18:00'},
        {'grupo': 'H', 'team1': 'Cabo Verde', 'team2': 'Arabia Saudita', 'date': '2026-06-26', 'time_str': '19:00'},
        {'grupo': 'H', 'team1': 'Uruguay', 'team2': 'España', 'date': '2026-06-26', 'time_str': '18:00'},
        {'grupo': 'I', 'team1': 'Francia', 'team2': 'Senegal', 'date': '2026-06-16', 'time_str': '15:00'},
        {'grupo': 'I', 'team1': 'Irak', 'team2': 'Noruega', 'date': '2026-06-16', 'time_str': '18:00'},
        {'grupo': 'I', 'team1': 'Francia', 'team2': 'Irak', 'date': '2026-06-22', 'time_str': '17:00'},
        {'grupo': 'I', 'team1': 'Noruega', 'team2': 'Senegal', 'date': '2026-06-22', 'time_str': '20:00'},
        {'grupo': 'I', 'team1': 'Noruega', 'team2': 'Francia', 'date': '2026-06-26', 'time_str': '15:00'},
        {'grupo': 'I', 'team1': 'Senegal', 'team2': 'Irak', 'date': '2026-06-26', 'time_str': '15:00'},
        {'grupo': 'J', 'team1': 'Argentina', 'team2': 'Argelia', 'date': '2026-06-16', 'time_str': '20:00'},
        {'grupo': 'J', 'team1': 'Austria', 'team2': 'Jordania', 'date': '2026-06-16', 'time_str': '21:00'},
        {'grupo': 'J', 'team1': 'Argentina', 'team2': 'Austria', 'date': '2026-06-22', 'time_str': '12:00'},
        {'grupo': 'J', 'team1': 'Jordania', 'team2': 'Argelia', 'date': '2026-06-22', 'time_str': '20:00'},
        {'grupo': 'J', 'team1': 'Argelia', 'team2': 'Austria', 'date': '2026-06-27', 'time_str': '21:00'},
        {'grupo': 'J', 'team1': 'Jordania', 'team2': 'Argentina', 'date': '2026-06-27', 'time_str': '21:00'},
        {'grupo': 'K', 'team1': 'Portugal', 'team2': 'RD Congo', 'date': '2026-06-17', 'time_str': '12:00'},
        {'grupo': 'K', 'team1': 'Uzbekistán', 'team2': 'Colombia', 'date': '2026-06-17', 'time_str': '20:00'},
        {'grupo': 'K', 'team1': 'Portugal', 'team2': 'Uzbekistán', 'date': '2026-06-23', 'time_str': '12:00'},
        {'grupo': 'K', 'team1': 'Colombia', 'team2': 'RD Congo', 'date': '2026-06-23', 'time_str': '20:00'},
        {'grupo': 'K', 'team1': 'Colombia', 'team2': 'Portugal', 'date': '2026-06-27', 'time_str': '19:30'},
        {'grupo': 'K', 'team1': 'RD Congo', 'team2': 'Uzbekistán', 'date': '2026-06-27', 'time_str': '19:30'},
        {'grupo': 'L', 'team1': 'Inglaterra', 'team2': 'Croacia', 'date': '2026-06-17', 'time_str': '15:00'},
        {'grupo': 'L', 'team1': 'Ghana', 'team2': 'Panamá', 'date': '2026-06-17', 'time_str': '19:00'},
        {'grupo': 'L', 'team1': 'Inglaterra', 'team2': 'Ghana', 'date': '2026-06-23', 'time_str': '16:00'},
        {'grupo': 'L', 'team1': 'Panamá', 'team2': 'Croacia', 'date': '2026-06-23', 'time_str': '19:00'},
        {'grupo': 'L', 'team1': 'Panamá', 'team2': 'Inglaterra', 'date': '2026-06-27', 'time_str': '17:00'},
        {'grupo': 'L', 'team1': 'Croacia', 'team2': 'Ghana', 'date': '2026-06-27', 'time_str': '17:00'},
    ]
    
    partidos_a_insertar = []
    
    for match in match_schedule_2026:
        # Parsing date "YYYY-MM-DD" and time "HH:MM"
        year, month, day = map(int, match['date'].split('-'))
        hour, minute = map(int, match['time_str'].split(':'))
        # Se ajusta la hora a la de Venezuela sumando 2 horas
        fecha_partido = datetime(year, month, day, hour, minute) + timedelta(hours=2)
        
        p = Partido(equipo_a=match['team1'], equipo_b=match['team2'], fecha=fecha_partido, fase="Fase de Grupos", grupo=match['grupo'])
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
