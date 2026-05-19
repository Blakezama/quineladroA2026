from app import app, db, Partido, Usuario, Voto
import random

with app.app_context():
    # Asegurarse de tener un par de usuarios para votar
    users = Usuario.query.all()
    if len(users) < 5:
        for i in range(1, 6):
            u = Usuario(nombre=f"Fan {i}", email=f"fan{i}@test.com")
            db.session.add(u)
        db.session.commit()
    
    users = Usuario.query.all()
    partidos = Partido.query.all()
    
    # Añadir votos aleatorios a los primeros 10 partidos para probar
    for i in range(20):
        if i >= len(partidos): break
        p = partidos[i]
        
        for u in users:
            # Crear voto aleatorio
            ganador = random.choice(['A', 'B', 'E', 'A', 'A']) # Sesgar
            am = random.choice(['A', 'B'])
            ro = random.choice(['A', 'B'])
            
            # Chequear si ya votó
            if not Voto.query.filter_by(usuario_id=u.id, partido_id=p.id).first():
                v = Voto(voto_ganador=ganador, voto_amarilla=am, voto_roja=ro, usuario_id=u.id, partido_id=p.id)
                db.session.add(v)
            
    db.session.commit()
    print("Votos simulados agregados para probar la UI prob-bar.")
