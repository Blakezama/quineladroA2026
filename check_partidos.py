import sqlite3
import os

db_path = os.path.join('instance', 'mundial.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, equipo_a, equipo_b, fecha, estado, goles_a, goles_b FROM partido LIMIT 10")
for row in cursor.fetchall():
    print(row)
    
conn.close()
