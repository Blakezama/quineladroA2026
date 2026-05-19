"""
add_passwords.py — Migración de base de datos para añadir contraseñas.

Pasos:
  1. Añade la columna password_hash a la tabla usuario (si no existe).
  2. Asigna la contraseña "231099" a los usuarios "prueba" y "brian".
  3. Asigna la contraseña por defecto "123456" al resto de usuarios.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'mundial.db')

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. Añadir columna password_hash si no existe ---
    cursor.execute("PRAGMA table_info(usuario)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'password_hash' not in columns:
        print("Añadiendo columna 'password_hash' a la tabla 'usuario'...")
        cursor.execute("ALTER TABLE usuario ADD COLUMN password_hash TEXT")
        conn.commit()
        print("  [OK] Columna añadida.")
    else:
        print("  [--] La columna 'password_hash' ya existe. Continuando...")

    # --- 2. Asignar contraseñas especiales ---
    SPECIAL_EMAILS_PASSWORDS = {
        'prueba@mundial.com': '231099',
        'brian@mundial.com':  '231099',
    }

    cursor.execute("SELECT id, email FROM usuario")
    usuarios = cursor.fetchall()

    for user_id, email in usuarios:
        if email in SPECIAL_EMAILS_PASSWORDS:
            raw_password = SPECIAL_EMAILS_PASSWORDS[email]
            label = "'{}' (especial)".format(raw_password)
        else:
            raw_password = '123456'
            label = "'123456' (por defecto)"

        hashed = generate_password_hash(raw_password)
        cursor.execute(
            "UPDATE usuario SET password_hash = ? WHERE id = ?",
            (hashed, user_id)
        )
        print("  [OK] Usuario #{} ({}) -> contrasena {}".format(user_id, email, label))

    conn.commit()
    conn.close()
    print("\n[DONE] Migracion completada correctamente.")

if __name__ == '__main__':
    main()
