"""
Corrige las fechas y horas de los Dieciseisavos de Final segun el calendario real de la FIFA.
Horas en VE (UTC-4).
"""
from app import app, db, Partido
from datetime import datetime

SCHEDULE = [
    # Dom 28 junio
    ("Sudafrica",      "Canada",                "2026-06-28 15:00:00"),  # placeholder key

    # Lun 29 junio
    ("Brasil",         "Japon",                 "2026-06-29 13:00:00"),
    ("Alemania",       "Paraguay",              "2026-06-29 16:30:00"),
    ("Paises Bajos",   "Marruecos",             "2026-06-29 21:00:00"),

    # Mar 30 junio
    ("Costa de Marfil","Noruega",               "2026-06-30 13:00:00"),
    ("Francia",        "Suecia",                "2026-06-30 17:00:00"),
    ("Mexico",         "Ecuador",               "2026-06-30 21:00:00"),

    # Mie 1 julio
    ("Portugal",       "Croacia",               "2026-07-01 13:00:00"),
    ("Espana",         "Austria",               "2026-07-01 17:00:00"),
    ("Estados Unidos", "Bosnia y Herzegovina",  "2026-07-01 21:00:00"),

    # Jue 2 julio
    ("Belgica",        "Senegal",               "2026-07-02 13:00:00"),
    ("Argentina",      "Cabo Verde",            "2026-07-02 17:00:00"),
    ("Colombia",       "Ghana",                 "2026-07-02 21:00:00"),

    # Vie 3 julio
    ("Inglaterra",     "RD Congo",              "2026-07-03 13:00:00"),
    ("Suiza",          "Argelia",               "2026-07-03 17:00:00"),
    ("Australia",      "Egipto",                "2026-07-03 21:00:00"),
]

# Mapeo de nombres simplificados a nombres reales en la BD
NAME_MAP = {
    "Sudafrica": "Sudafrica",
    "Canada": "Canada",
    "Brasil": "Brasil",
    "Japon": "Japon",
    "Alemania": "Alemania",
    "Paraguay": "Paraguay",
    "Paises Bajos": "Paises Bajos",
    "Marruecos": "Marruecos",
    "Costa de Marfil": "Costa de Marfil",
    "Noruega": "Noruega",
    "Francia": "Francia",
    "Suecia": "Suecia",
    "Mexico": "Mexico",
    "Ecuador": "Ecuador",
    "Portugal": "Portugal",
    "Croacia": "Croacia",
    "Espana": "Espana",
    "Austria": "Austria",
    "Estados Unidos": "Estados Unidos",
    "Bosnia y Herzegovina": "Bosnia y Herzegovina",
    "Belgica": "Belgica",
    "Senegal": "Senegal",
    "Argentina": "Argentina",
    "Cabo Verde": "Cabo Verde",
    "Colombia": "Colombia",
    "Ghana": "Ghana",
    "Inglaterra": "Inglaterra",
    "RD Congo": "RD Congo",
    "Suiza": "Suiza",
    "Argelia": "Argelia",
    "Australia": "Australia",
    "Egipto": "Egipto",
}

def fix_matches():
    with app.app_context():
        actualizados = 0
        no_encontrados = []

        # Get all dieciseisavos matches
        partidos = Partido.query.filter_by(fase="Dieciseisavos de Final").all()
        print(f"Partidos en BD: {len(partidos)}")
        for p in partidos:
            print(f"  - ID {p.id}: {p.equipo_a} vs {p.equipo_b} | {p.fecha}")

        print("\nActualizando fechas...")
        for eq_a_key, eq_b_key, date_str in SCHEDULE:
            fecha = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

            # Search with LIKE to handle accented chars
            partido = None
            for p in partidos:
                a_match = eq_a_key.lower() in p.equipo_a.lower() or p.equipo_a.lower() in eq_a_key.lower()
                b_match = eq_b_key.lower() in p.equipo_b.lower() or p.equipo_b.lower() in eq_b_key.lower()
                ab_match = a_match and b_match

                ba_match_a = eq_b_key.lower() in p.equipo_a.lower() or p.equipo_a.lower() in eq_b_key.lower()
                ba_match_b = eq_a_key.lower() in p.equipo_b.lower() or p.equipo_b.lower() in eq_a_key.lower()
                ba_match = ba_match_a and ba_match_b

                if ab_match or ba_match:
                    partido = p
                    break

            if partido:
                partido.fecha = fecha
                actualizados += 1
                print(f"  OK: {partido.equipo_a} vs {partido.equipo_b} -> {fecha.strftime('%d/%m/%Y %H:%M')}")
            else:
                no_encontrados.append(f"{eq_a_key} vs {eq_b_key}")

        db.session.commit()
        print(f"\nActualizados: {actualizados}")
        if no_encontrados:
            print(f"No encontrados ({len(no_encontrados)}): {no_encontrados}")

if __name__ == '__main__':
    fix_matches()
