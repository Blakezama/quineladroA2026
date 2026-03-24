import sqlite3
import os

db_path = os.path.join('instance', 'mundial.db')

if not os.path.exists(db_path):
    print(f"Error: No se encontro el archivo en {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Consultamos los usuarios
        cursor.execute("SELECT * FROM usuario")
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("No hay usuarios registrados aun.")
        else:
            print("\n--- USUARIOS REGISTRADOS ---")
            for u in usuarios:
                print(f"ID: {u[0]} | Nombre: {u[1]} | Email: {u[2]}")
                
        # Consultamos las predicciones también para dar más info
        cursor.execute("SELECT * FROM prediccion")
        predicciones = cursor.fetchall()
        
        if predicciones:
            print("\n--- PREDICCIONES REALIZADAS ---")
            for p in predicciones:
                print(f"ID: {p[0]} | Usuario ID: {p[4]} | Local: {p[1]} - Visitante: {p[2]}")
                
        conn.close()
    except Exception as e:
        print(f"Error al leer la base de datos: {e}")
