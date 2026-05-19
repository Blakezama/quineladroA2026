import sqlite3
import os

db_path = os.path.join('instance', 'mundial.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE voto ADD COLUMN goles_a_prediccion INTEGER;")
        print("Columna 'goles_a_prediccion' añadida exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna 'goles_a_prediccion' ya existe.")
        else:
            print(f"Error: {e}")
            
    try:
        cursor.execute("ALTER TABLE voto ADD COLUMN goles_b_prediccion INTEGER;")
        print("Columna 'goles_b_prediccion' añadida exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna 'goles_b_prediccion' ya existe.")
        else:
            print(f"Error: {e}")
            
    try:
        cursor.execute("ALTER TABLE voto ADD COLUMN fecha_voto DATETIME;")
        print("Columna 'fecha_voto' añadida exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna 'fecha_voto' ya existe.")
        else:
            print(f"Error: {e}")
            
    try:
        cursor.execute("DROP TABLE IF EXISTS prediccion;")
        print("Tabla 'prediccion' eliminada exitosamente (si existía).")
    except sqlite3.OperationalError as e:
        print(f"Error al eliminar 'prediccion': {e}")
        
    conn.commit()
    conn.close()
else:
    print(f"No se encontró la base de datos en {db_path}")
