import sqlite3
import os

db_path = os.path.join('instance', 'mundial.db')
if not os.path.exists(db_path):
    db_path = 'mundial.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE partido ADD COLUMN amarilla_real VARCHAR(1)")
    print("Columna amarilla_real añadida.")
except Exception as e:
    print("Error amarilla:", e)

try:
    cur.execute("ALTER TABLE partido ADD COLUMN roja_real VARCHAR(1)")
    print("Columna roja_real añadida.")
except Exception as e:
    print("Error roja:", e)

try:
    cur.execute("UPDATE partido SET estado = 'finished', goles_a = 2, goles_b = 1, amarilla_real = 'A', roja_real = 'B' WHERE equipo_a = 'México' AND equipo_b = 'Sudáfrica'")
    print("Updated México vs Sudáfrica to test data.")
except Exception as e:
    print("Error update:", e)

conn.commit()
conn.close()
