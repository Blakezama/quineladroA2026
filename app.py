from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import locale

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_secreto_super_seguro_para_mvp'  # Necesario para sesiones y flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mundial.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

db = SQLAlchemy(app)

# ==========================================
# 0. ARQUITECTURA DE DATOS (DATA-DRIVEN)
# ==========================================
MUNDIAL_DATA = {
    'Grupos': {
        'A': [
            {'nombre': 'México', 'code': 'mx', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Santiago Giménez', 'pos': 'Delantero'}, {'nombre': 'Edson Álvarez', 'pos': 'Mediocampista'}, {'nombre': 'Guillermo Ochoa', 'pos': 'Portero'}]},
            {'nombre': 'Sudáfrica', 'code': 'za', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Percy Tau', 'pos': 'Delantero'}, {'nombre': 'Ronwen Williams', 'pos': 'Portero'}, {'nombre': 'Teboho Mokoena', 'pos': 'Mediocampista'}]},
            {'nombre': 'Corea del Sur', 'code': 'kr', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Son Heung-min', 'pos': 'Delantero'}, {'nombre': 'Kim Min-jae', 'pos': 'Defensa'}, {'nombre': 'Lee Kang-in', 'pos': 'Mediocampista'}]},
            {'nombre': 'Por determinar...', 'code': 'un', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Jugador X', 'pos': '???'}, {'nombre': 'Jugador Y', 'pos': '???'}, {'nombre': 'Jugador Z', 'pos': '???'}]}
        ],
        'B': [
            {'nombre': 'Canadá', 'code': 'ca', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Alphonso Davies', 'pos': 'Defensa'}, {'nombre': 'Jonathan David', 'pos': 'Delantero'}, {'nombre': 'Stephen Eustáquio', 'pos': 'Mediocampista'}]},
            {'nombre': 'Por determinar...', 'code': 'un', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Jugador X', 'pos': '???'}, {'nombre': 'Jugador Y', 'pos': '???'}, {'nombre': 'Jugador Z', 'pos': '???'}]},
            {'nombre': 'Catar', 'code': 'qa', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Suiza', 'code': 'ch', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'C': [
            {'nombre': 'Brasil', 'code': 'br', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Marruecos', 'code': 'ma', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Haití', 'code': 'ht', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Escocia', 'code': 'gb-sct', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'D': [
            {'nombre': 'Estados Unidos', 'code': 'us', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Christian Pulisic', 'pos': 'Delantero'}, {'nombre': 'Weston McKennie', 'pos': 'Mediocampista'}, {'nombre': 'Tyler Adams', 'pos': 'Mediocampista'}]},
            {'nombre': 'Paraguay', 'code': 'py', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Miguel Almirón', 'pos': 'Mediocampista'}, {'nombre': 'Julio Enciso', 'pos': 'Delantero'}, {'nombre': 'Gustavo Gómez', 'pos': 'Defensa'}]},
            {'nombre': 'Australia', 'code': 'au', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Por determinar...', 'code': 'un', 'pj': 0, 'pts': 0, 'jugadores': [{'nombre': 'Jugador X', 'pos': '???'}, {'nombre': 'Jugador Y', 'pos': '???'}, {'nombre': 'Jugador Z', 'pos': '???'}]}
        ],
        'E': [
            {'nombre': 'Alemania', 'code': 'de', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Ecuador', 'code': 'ec', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Costa de Marfil', 'code': 'ci', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Curazao', 'code': 'cw', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'F': [
            {'nombre': 'Países Bajos', 'code': 'nl', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Japón', 'code': 'jp', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Por determinar...', 'code': 'un', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Túnez', 'code': 'tn', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'G': [
            {'nombre': 'Bélgica', 'code': 'be', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Egipto', 'code': 'eg', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Irán', 'code': 'ir', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Nueva Zelanda', 'code': 'nz', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'H': [
            {'nombre': 'España', 'code': 'es', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Cabo Verde', 'code': 'cv', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Arabia Saudita', 'code': 'sa', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Uruguay', 'code': 'uy', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'I': [
            {'nombre': 'Francia', 'code': 'fr', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Senegal', 'code': 'sn', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Por determinar...', 'code': 'un', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Noruega', 'code': 'no', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'J': [
            {'nombre': 'Argentina', 'code': 'ar', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Argelia', 'code': 'dz', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Austria', 'code': 'at', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Jordania', 'code': 'jo', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'K': [
            {'nombre': 'Portugal', 'code': 'pt', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Por determinar...', 'code': 'un', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Uzbekistán', 'code': 'uz', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Colombia', 'code': 'co', 'pj': 0, 'pts': 0, 'jugadores': []}
        ],
        'L': [
            {'nombre': 'Inglaterra', 'code': 'gb-eng', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Croacia', 'code': 'hr', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Ghana', 'code': 'gh', 'pj': 0, 'pts': 0, 'jugadores': []},
            {'nombre': 'Panamá', 'code': 'pa', 'pj': 0, 'pts': 0, 'jugadores': []}
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
    # Relación inversa para saber qué predicciones y votos hizo un usuario
    predicciones = db.relationship('Prediccion', backref='usuario', lazy=True)
    votos = db.relationship('Voto', backref='usuario', lazy=True)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipo_a = db.Column(db.String(50), nullable=False)
    equipo_b = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    grupo = db.Column(db.String(10), nullable=True) # ej: 'A', 'B'
    fase = db.Column(db.String(50), nullable=False) # ej: 'Fase de Grupos'
    predicciones = db.relationship('Prediccion', backref='partido', lazy=True)

class Prediccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marcador_local = db.Column(db.Integer, nullable=False)
    marcador_visitante = db.Column(db.Integer, nullable=False)
    anotador_primer_gol = db.Column(db.String(100), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)

class Voto(db.Model):
    """Modelo de votación única por partido. Almacena predicción de ganador y tarjetas."""
    id = db.Column(db.Integer, primary_key=True)
    voto_ganador = db.Column(db.String(1), nullable=False)    # 'A' o 'B'
    voto_amarilla = db.Column(db.String(1), nullable=False)   # 'A' o 'B'
    voto_roja = db.Column(db.String(1), nullable=False)       # 'A' o 'B'
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)
    
    # Relación para acceder a los datos del partido desde el voto
    partido = db.relationship('Partido', backref=db.backref('votos_rel', lazy=True))

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
    # Extraemos country_codes y jugadores de la estructura central
    country_codes = {}
    jugadores_mock = {}
    for grupo_id, equipos in MUNDIAL_DATA['Grupos'].items():
        for eq in equipos:
            country_codes[eq['nombre']] = eq['code']
            jugadores_mock[eq['nombre']] = eq['jugadores']
        
    return dict(usuario_actual=usuario_actual, fecha_actual=ahora, country_codes=country_codes, jugadores_mock=jugadores_mock, MUNDIAL_DATA=MUNDIAL_DATA)

# ==========================================
# 3. RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            session.permanent = True
            session['usuario_id'] = usuario.id
            flash(f'Bienvenido de nuevo, {usuario.nombre}!', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Email no encontrado. ¿Ya te registraste?', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('inicio'))

# ==========================================
# 4. RUTAS PRINCIPALES
# ==========================================

@app.route('/')
def inicio():
    """Página de inicio que lista los partidos del Mundial."""
    partidos_db = Partido.query.all()
    partidos_json = []
    for p in partidos_db:
        partidos_json.append({
            'id': p.id,
            'equipo_a': p.equipo_a,
            'equipo_b': p.equipo_b,
            'fecha': p.fecha.isoformat(),
            'grupo': p.grupo,
            'fase': p.fase
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
        
        # Validar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Este correo electrónico ya está registrado.', 'error')
            return redirect(url_for('registro'))
            
        # Crear y guardar nuevo usuario
        nuevo_usuario = Usuario(nombre=nombre, email=email)
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
    """Permite al usuario actualizar su foto de perfil."""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    usuario = Usuario.query.get(session['usuario_id'])
    nueva_foto = request.form.get('foto_url')
    
    if nueva_foto:
        usuario.foto_perfil = nueva_foto
        db.session.commit()
        flash('Foto de perfil actualizada.', 'success')
    else:
        # Si no pone nada, podemos dejarle elegir la de 500x500 generada
        # O simplemente no hacer nada. El usuario pidió una de 500x500 o la default.
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
        return {'total': 0, 'ganador': {'A': 50, 'B': 50}, 'amarilla': {'A': 50, 'B': 50}, 'roja': {'A': 50, 'B': 50}}
    
    g_a = sum(1 for v in votos if v.voto_ganador == 'A')
    am_a = sum(1 for v in votos if v.voto_amarilla == 'A')
    ro_a = sum(1 for v in votos if v.voto_roja == 'A')
    
    return {
        'total': total,
        'ganador': {'A': round((g_a / total) * 100), 'B': round(((total - g_a) / total) * 100)},
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
    
    if ganador not in ('A', 'B') or amarilla not in ('A', 'B') or roja not in ('A', 'B'):
        return jsonify({'error': 'Valores inválidos. Deben ser A o B.'}), 400
    
    nuevo_voto = Voto(
        voto_ganador=ganador,
        voto_amarilla=amarilla,
        voto_roja=roja,
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
            'roja': roja
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
                'roja': voto_existente.voto_roja
            }
            
    return jsonify({
        'porcentajes': porcentajes,
        'mi_voto': mi_voto
    })


# ==========================================
# 3. SEMILLA DE DATOS (PARA PRUEBAS)
# ==========================================
def poblar_datos_iniciales():
    """Crea datos iniciales en la DB para probar el MVP si está vacía."""
    # Limpiamos las tablas relacionadas a partidos para asegurar la sincronización
    try:
        Prediccion.query.delete()
        Partido.query.delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al limpiar datos de prueba: {e}")

    # Chequeamos el usuario mock
    if not Usuario.query.filter_by(email="prueba@mundial.com").first():
        u1 = Usuario(nombre="Usuario Prueba", email="prueba@mundial.com")
        db.session.add(u1)
        
    # Partidos de prueba basados en el nuevo cronograma oficial
    # Partido 1: México vs. Sudáfrica (11/06/2026 - 15:00)
    p1 = Partido(equipo_a="México", equipo_b="Sudáfrica", fecha=datetime(2026, 6, 11, 15, 0), fase="Fase de Grupos", grupo="A")
    # Partido 2: Corea del Sur vs. Equipo por definir (11/06/2026 - 22:00)
    p2 = Partido(equipo_a="Corea del Sur", equipo_b="Por determinar...", fecha=datetime(2026, 6, 11, 22, 0), fase="Fase de Grupos", grupo="A")
    # Partido 3: Canadá vs. Equipo por definir (12/06/2026 - 15:00)
    p3 = Partido(equipo_a="Canadá", equipo_b="Por determinar...", fecha=datetime(2026, 6, 12, 15, 0), fase="Fase de Grupos", grupo="B")
    # Partido 4: Estados Unidos vs. Paraguay (12/06/2026 - 21:00)
    p4 = Partido(equipo_a="Estados Unidos", equipo_b="Paraguay", fecha=datetime(2026, 6, 12, 21, 0), fase="Fase de Grupos", grupo="D")
    
    db.session.add_all([p1, p2, p3, p4])
    db.session.commit()
    print("Base de datos sincronizada con el nuevo cronograma de partidos.")

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
