from app import app, db, poblar_datos_iniciales

with app.app_context():
    print("Iniciando repoblación masiva a 72 partidos de fase de grupos...")
    poblar_datos_iniciales()
    print("Repoblación masiva finalizada.")
