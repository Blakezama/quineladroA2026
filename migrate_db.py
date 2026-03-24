import sqlite3
import os

db_path = os.path.join('instance', 'mundial.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE usuario ADD COLUMN foto_perfil VARCHAR(255) DEFAULT 'img/default_perfil.png';")
        conn.commit()
        print("Columna 'foto_perfil' añadida exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna 'foto_perfil' ya existe.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"No se encontró la base de datos en {db_path}")
