from app import app, db, Partido

with app.app_context():
    partidos = Partido.query.filter_by(fase="Dieciseisavos de Final").order_by(Partido.fecha).all()
    print("Estado actual de los Dieciseisavos de Final:")
    for p in partidos:
        print(f"  ID {p.id}: {p.equipo_a} vs {p.equipo_b} | {p.fecha.strftime('%d/%m/%Y %H:%M')}")
