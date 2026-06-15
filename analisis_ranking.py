import sqlite3
import os

db_path = os.path.join('instance', 'mundial.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

users = {row['id']: dict(row) for row in cursor.execute('SELECT * FROM usuario').fetchall()}

matches = {}
for row in cursor.execute('SELECT * FROM partido WHERE estado = "finished"').fetchall():
    match = dict(row)
    if match['goles_a'] is None: match['goles_a'] = 0
    if match['goles_b'] is None: match['goles_b'] = 0
    
    if match['goles_a'] > match['goles_b']:
        match['ganador_real'] = 'A'
    elif match['goles_b'] > match['goles_a']:
        match['ganador_real'] = 'B'
    else:
        match['ganador_real'] = 'E'
    matches[match['id']] = match

votes = cursor.execute('SELECT * FROM voto').fetchall()

print(f'Total partidos finalizados: {len(matches)}')
if len(matches) == 0:
    print('No hay partidos finalizados aun para analizar.')
else:
    for m_id, m in matches.items():
        print(f'- Partido {m_id}: {m["equipo_a"]} {m["goles_a"]} vs {m["goles_b"]} {m["equipo_b"]} (Ganador real: {m["ganador_real"]})')

print('\n--- Análisis de Votos y Puntos ---')
user_points = {u_id: {'puntos': 0, 'exactos': 0, 'ganadores': 0, 'votos_procesados': 0} for u_id in users}

hay_votos = False
for vote in votes:
    vote = dict(vote)
    u_id = vote['usuario_id']
    m_id = vote['partido_id']
    
    if m_id in matches:
        hay_votos = True
        m = matches[m_id]
        user_points[u_id]['votos_procesados'] += 1
        
        # Validar predicciones none
        g_a_pred = vote['goles_a_prediccion'] if vote['goles_a_prediccion'] is not None else 0
        g_b_pred = vote['goles_b_prediccion'] if vote['goles_b_prediccion'] is not None else 0
        
        acerto_marcador = (g_a_pred == m['goles_a'] and g_b_pred == m['goles_b'])
        acerto_ganador = (vote['voto_ganador'] == m['ganador_real'])
        
        pts = 0
        if acerto_marcador:
            pts = 5
            user_points[u_id]['exactos'] += 1
            user_points[u_id]['puntos'] += 5
        elif acerto_ganador:
            pts = 3
            user_points[u_id]['ganadores'] += 1
            user_points[u_id]['puntos'] += 3
            
        print(f'Usuario {users[u_id]["nombre"]} votó para el Partido {m_id} ({m["equipo_a"]} vs {m["equipo_b"]}):')
        print(f'  Predicción: {vote["voto_ganador"]} (Goles: {g_a_pred}-{g_b_pred})')
        print(f'  Resultado real: {m["ganador_real"]} (Goles: {m["goles_a"]}-{m["goles_b"]})')
        print(f'  Puntos obtenidos en este partido: {pts}')

if not hay_votos:
    print('No hay votos realizados en los partidos finalizados.')

print('\n--- Ranking Global ---')
ranking = sorted([ (u_id, data) for u_id, data in user_points.items() ], key=lambda x: (-x[1]['puntos'], -x[1]['exactos'], -x[1]['ganadores']))
for i, (u_id, data) in enumerate(ranking, 1):
    print(f'{i}. {users[u_id]["nombre"]}: {data["puntos"]} pts (Exactos: {data["exactos"]}, Por ganador: {data["ganadores"]}, Votos finalizados procesados: {data["votos_procesados"]})')

conn.close()
