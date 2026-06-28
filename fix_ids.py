"""
Corrige por ID los partidos que no se actualizaron por caracteres acentuados.
IDs extraidos del output anterior.
"""
from app import app, db, Partido
from datetime import datetime

# (id, fecha_hora VE)
FIXES = [
    (2451, "2026-06-28 15:00:00"),  # Sudafrica vs Canada
    (2457, "2026-06-29 13:00:00"),  # Brasil vs Japon
    (2452, "2026-06-29 21:00:00"),  # Paises Bajos vs Marruecos
    (2459, "2026-06-30 21:00:00"),  # Mexico vs Ecuador
    (2454, "2026-07-01 17:00:00"),  # Espana vs Austria
    (2456, "2026-07-02 13:00:00"),  # Belgica vs Senegal
]

with app.app_context():
    for pid, date_str in FIXES:
        p = Partido.query.get(pid)
        if p:
            p.fecha = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            print(f"  OK ID {pid}: {p.equipo_a} vs {p.equipo_b} -> {date_str}")
        else:
            print(f"  ERROR: ID {pid} no encontrado")
    db.session.commit()
    print("Listo!")
