from app import app, db, Partido
from datetime import datetime

MATCHES = [
    ("Alemania", "Paraguay", "2026-06-28 12:00:00"),
    ("Francia", "Suecia", "2026-06-28 16:00:00"),
    ("Sudáfrica", "Canadá", "2026-06-28 19:00:00"),
    ("Países Bajos", "Marruecos", "2026-06-28 22:00:00"),
    
    ("Portugal", "Croacia", "2026-06-29 12:00:00"),
    ("España", "Austria", "2026-06-29 16:00:00"),
    ("Estados Unidos", "Bosnia y Herzegovina", "2026-06-29 19:00:00"),
    ("Bélgica", "Senegal", "2026-06-29 22:00:00"),
    
    ("Brasil", "Japón", "2026-06-30 12:00:00"),
    ("Costa de Marfil", "Noruega", "2026-06-30 16:00:00"),
    ("México", "Ecuador", "2026-06-30 19:00:00"),
    ("Inglaterra", "RD Congo", "2026-06-30 22:00:00"),
    
    ("Argentina", "Cabo Verde", "2026-07-01 12:00:00"),
    ("Australia", "Egipto", "2026-07-01 16:00:00"),
    ("Suiza", "Argelia", "2026-07-01 19:00:00"),
    ("Colombia", "Ghana", "2026-07-01 22:00:00")
]

def add_matches():
    with app.app_context():
        for eq_a, eq_b, date_str in MATCHES:
            fecha = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            # Check if match already exists
            exist = Partido.query.filter_by(equipo_a=eq_a, equipo_b=eq_b, fase="Dieciseisavos de Final").first()
            if not exist:
                p = Partido(
                    equipo_a=eq_a,
                    equipo_b=eq_b,
                    fecha=fecha,
                    fase="Dieciseisavos de Final",
                    estado="scheduled"
                )
                db.session.add(p)
                print(f"Added {eq_a} vs {eq_b}")
            else:
                exist.fecha = fecha
                print(f"Updated {eq_a} vs {eq_b}")
        
        db.session.commit()
        print("Done!")

if __name__ == '__main__':
    add_matches()
