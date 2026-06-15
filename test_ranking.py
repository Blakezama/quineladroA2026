import sqlite3
import os

db_path = os.path.join('instance', 'mundial.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get users
users = {row['id']: dict(row) for row in cursor.execute('SELECT * FROM usuario').fetchall()}

print("=== ESTADO ACTUAL DE VOTOS ===")
votes = cursor.execute('SELECT * FROM voto').fetchall()
if not votes:
    print("No hay votos en la base de datos.")
else:
    for vote in votes:
        vote = dict(vote)
        u_nombre = users[vote['usuario_id']]['nombre'] if vote['usuario_id'] in users else f"ID {vote['usuario_id']}"
        m_id = vote['partido_id']
        partido = cursor.execute('SELECT * FROM partido WHERE id = ?', (m_id,)).fetchone()
        equipo_a = partido['equipo_a'] if partido else 'Equipo A'
        equipo_b = partido['equipo_b'] if partido else 'Equipo B'
        estado = partido['estado'] if partido else 'Desconocido'
        g_a_pred = vote['goles_a_prediccion']
        g_b_pred = vote['goles_b_prediccion']
        
        print(f"El usuario '{u_nombre}' votó para {equipo_a} vs {equipo_b} (Partido {m_id}, Estado actual: {estado}):")
        print(f"   -> Predicción ganador: {vote['voto_ganador']}, Goles: {g_a_pred}-{g_b_pred}")

print("\n=== SIMULACIÓN DEL RANKING ===")
print("Si asumiéramos que el partido 1 termina 2-0 a favor de México (Equipo A), los puntos serían:")

m = {'goles_a': 2, 'goles_b': 0, 'ganador_real': 'A'}
for vote in votes:
    vote = dict(vote)
    if vote['partido_id'] == 1:
        u_nombre = users[vote['usuario_id']]['nombre'] if vote['usuario_id'] in users else f"ID {vote['usuario_id']}"
        g_a_pred = vote['goles_a_prediccion']
        g_b_pred = vote['goles_b_prediccion']
        
        acerto_marcador = (g_a_pred == m['goles_a'] and g_b_pred == m['goles_b'])
        acerto_ganador = (vote['voto_ganador'] == m['ganador_real'])
        
        pts = 0
        if acerto_marcador: pts = 5
        elif acerto_ganador: pts = 3
        
        print(f"Usuario {u_nombre}: Puntos obtenidos = {pts} (Por acertar ganador? {acerto_ganador}, Por acertar exacto? {acerto_marcador})")

conn.close()
