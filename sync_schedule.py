"""
sync_schedule.py
Sincroniza las fechas/horarios de los partidos del Mundial 2026
usando TheStatsAPI (100% gratis, sin key, sin registro).

Uso: python sync_schedule.py
"""
import requests
from datetime import datetime, timezone, timedelta
from app import app, db, Partido

# Mapeo de nombres en inglés (TheStatsAPI) → español (tu BD)
TEAM_NAME_MAP = {
    "Mexico": "México",
    "South Africa": "Sudáfrica",
    "South Korea": "Corea del Sur",
    "Korea Republic": "Corea del Sur",
    "Czech Republic": "Chequia",
    "Czechia": "Chequia",
    "Canada": "Canadá",
    "Bosnia and Herzegovina": "Bosnia y Herzegovina",
    "Qatar": "Catar",
    "Switzerland": "Suiza",
    "Brazil": "Brasil",
    "Morocco": "Marruecos",
    "Haiti": "Haití",
    "Scotland": "Escocia",
    "United States": "Estados Unidos",
    "Paraguay": "Paraguay",
    "Australia": "Australia",
    "Turkey": "Turquía",
    "Turkiye": "Turquía",
    "Germany": "Alemania",
    "Ecuador": "Ecuador",
    "Ivory Coast": "Costa de Marfil",
    "Cote d'Ivoire": "Costa de Marfil",
    "Curacao": "Curazao",
    "Netherlands": "Países Bajos",
    "Japan": "Japón",
    "Sweden": "Suecia",
    "Tunisia": "Túnez",
    "Belgium": "Bélgica",
    "Egypt": "Egipto",
    "Iran": "Irán",
    "IR Iran": "Irán",
    "New Zealand": "Nueva Zelanda",
    "Spain": "España",
    "Cape Verde": "Cabo Verde",
    "Saudi Arabia": "Arabia Saudita",
    "Uruguay": "Uruguay",
    "France": "Francia",
    "Senegal": "Senegal",
    "Iraq": "Irak",
    "Norway": "Noruega",
    "Argentina": "Argentina",
    "Algeria": "Argelia",
    "Austria": "Austria",
    "Jordan": "Jordania",
    "Portugal": "Portugal",
    "DR Congo": "RD Congo",
    "Congo DR": "RD Congo",
    "Democratic Republic of Congo": "RD Congo",
    "Uzbekistan": "Uzbekistán",
    "Colombia": "Colombia",
    "England": "Inglaterra",
    "Croatia": "Croacia",
    "Ghana": "Ghana",
    "Panama": "Panamá",
    "Serbia": "Serbia",
    "Denmark": "Dinamarca",
    "Indonesia": "Indonesia",
    "Nigeria": "Nigeria",
    "Kenya": "Kenia",
    "Ukraine": "Ucrania",
    "Venezuela": "Venezuela",
    "Chile": "Chile",
    "Peru": "Perú",
    "Honduras": "Honduras",
    "Costa Rica": "Costa Rica",
    "Mali": "Malí",
    "Cameroon": "Camerún",
    "Poland": "Polonia",
    "Wales": "Gales",
    "Togo": "Togo",
    "Iceland": "Islandia",
    "Greece": "Grecia",
}

FASE_MAP = {
    "group-stage": "Fase de Grupos",
    "round-of-32": "Dieciseisavos de Final",
    "round-of-16": "Octavos de Final",
    "quarter-finals": "Cuartos de Final",
    "semi-finals": "Semifinales",
    "third-place": "Tercer Puesto",
    "final": "Final",
}

OFFSET_VENEZUELA = timedelta(hours=-4)  # UTC-4


def traducir(nombre_en):
    return TEAM_NAME_MAP.get(nombre_en, nombre_en)


def sync_schedule():
    print("Descargando calendario del Mundial 2026 desde TheStatsAPI...")
    try:
        resp = requests.get(
            "https://www.thestatsapi.com/world-cup/data/fixtures.json",
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] Error al descargar el calendario: {e}")
        return

    fixtures = data.get("fixtures", [])
    print(f"✅ {len(fixtures)} partidos recibidos desde la API.")

    actualizados = 0
    no_encontrados = []

    with app.app_context():
        for fix in fixtures:
            home_en = fix.get("homeTeam", "")
            away_en = fix.get("awayTeam", "")
            kickoff_utc_str = fix.get("kickoffUtc", "")
            stage_en = fix.get("stage", "group-stage")
            grupo = fix.get("group", None)  # puede ser None en eliminatorias

            home_es = traducir(home_en)
            away_es = traducir(away_en)
            fase_es = FASE_MAP.get(stage_en, "Fase de Grupos")

            # Parsear fecha UTC
            try:
                # Formato: "2026-06-11T19:00:00Z"
                kickoff_utc = datetime.strptime(kickoff_utc_str, "%Y-%m-%dT%H:%M:%SZ")
                # Convertir a hora Venezuela (UTC-4) para guardar consistente con la BD
                kickoff_ve = kickoff_utc + OFFSET_VENEZUELA
            except Exception:
                print(f"  ⚠️  Fecha inválida para {home_es} vs {away_es}: {kickoff_utc_str}")
                continue

            # Buscar el partido en la BD (por equipos, en ambas direcciones)
            partido = Partido.query.filter(
                ((Partido.equipo_a == home_es) & (Partido.equipo_b == away_es)) |
                ((Partido.equipo_a == away_es) & (Partido.equipo_b == home_es))
            ).first()

            if partido:
                # Actualizar fecha y fase
                partido.fecha = kickoff_ve
                if grupo:
                    partido.grupo = grupo.replace("group-", "").upper()
                partido.fase = fase_es
                actualizados += 1
                print(f"  ✅ {home_es} vs {away_es} → {kickoff_ve.strftime('%d/%m/%Y %H:%M')} VE")
            else:
                no_encontrados.append(f"{home_es} vs {away_es}")

        db.session.commit()

    print(f"\n{'='*50}")
    print(f"✅ Partidos actualizados: {actualizados}")
    if no_encontrados:
        print(f"⚠️  No encontrados en BD ({len(no_encontrados)}):")
        for nf in no_encontrados:
            print(f"   - {nf}")
    print("Sincronización completada.")


if __name__ == "__main__":
    sync_schedule()
