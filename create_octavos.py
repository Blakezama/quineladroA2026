from app import app, db, Partido
from datetime import datetime, timedelta

def get_winner(partido):
    if partido.estado == 'finished':
        if partido.goles_a is not None and partido.goles_b is not None:
            if partido.goles_a > partido.goles_b:
                return partido.equipo_a
            elif partido.goles_b > partido.goles_a:
                return partido.equipo_b
            else:
                return 'Por definir (Penales)' # Or something similar
    return 'Por definir'

with app.app_context():
    # Obtener los 16 partidos de dieciseisavos ordenados por fecha
    d16_matches = Partido.query.filter_by(fase='Dieciseisavos de Final').order_by(Partido.fecha).all()
    
    # Validar que haya exactamente 16 partidos
    if len(d16_matches) != 16:
        print(f"Error: Se esperaban 16 partidos de Dieciseisavos, se encontraron {len(d16_matches)}")
    else:
        # Fechas base para los octavos (ejemplo: 4 de julio al 7 de julio, 2 por día)
        base_date = datetime(2026, 7, 4, 13, 0)
        
        # Crear los 8 partidos de octavos
        for i in range(8):
            m1 = d16_matches[i * 2]
            m2 = d16_matches[i * 2 + 1]
            
            equipo_a = get_winner(m1)
            equipo_b = get_winner(m2)
            
            # Fecha del partido
            dias_offset = i // 2
            horas_offset = 0 if i % 2 == 0 else 4 # 13:00 y 17:00
            fecha_partido = base_date + timedelta(days=dias_offset, hours=horas_offset)
            
            nuevo_partido = Partido(
                fase='Octavos de Final',
                equipo_a=equipo_a,
                equipo_b=equipo_b,
                fecha=fecha_partido,
                estado='scheduled',
                grupo='Knockout'
            )
            db.session.add(nuevo_partido)
            print(f"Creado: {equipo_a} vs {equipo_b} el {fecha_partido}")
        
        db.session.commit()
        print("Partidos de Octavos de Final creados con éxito.")
