import sqlite3
import os

db_path = os.path.join('instance', 'mundial.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("UPDATE usuario SET is_admin = 1 WHERE email = 'prueba@mundial.com'")
conn.commit()
conn.close()
print("Usuario prueba@mundial.com configurado como administrador.")
