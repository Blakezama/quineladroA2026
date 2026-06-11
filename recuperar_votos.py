import sqlite3
import datetime

def main():
    conn_new = sqlite3.connect('instance/mundial.db')
    c_new = conn_new.cursor()

    conn_old = sqlite3.connect('copiabasededatos/mundial.db')
    c_old = conn_old.cursor()

    try:
        c_old.execute('SELECT * FROM voto')
        votos = c_old.fetchall()
        
        # Averiguar qué columnas tiene la tabla vieja
        columnas = [description[0] for description in c_old.description]
        
        insertados = 0
        for v in votos:
            # Crear un diccionario con los valores de la fila vieja
            fila = dict(zip(columnas, v))
            
            # Extraer valores, con defaults si no existen en la tabla vieja
            vgan = fila.get('voto_ganador')
            vama = fila.get('voto_amarilla', 'X')
            vroj = fila.get('voto_roja', 'X')
            goles_a = fila.get('goles_a_prediccion', None)
            goles_b = fila.get('goles_b_prediccion', None)
            fecha_voto = fila.get('fecha_voto', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.000000'))
            uid = fila.get('usuario_id')
            pid = fila.get('partido_id')
            
            try:
                c_new.execute('''
                    INSERT INTO voto (voto_ganador, voto_amarilla, voto_roja, goles_a_prediccion, goles_b_prediccion, fecha_voto, usuario_id, partido_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (vgan, vama, vroj, goles_a, goles_b, fecha_voto, uid, pid))
                insertados += 1
            except Exception as e:
                print(f"No se pudo insertar voto (usuario {uid}, partido {pid}): {e}")

        conn_new.commit()
        print(f"¡Éxito! Recuperados {insertados} votos de la copia de seguridad.")
        
    except Exception as e:
        print(f"Error general: {e}")
        
    conn_new.close()
    conn_old.close()

if __name__ == '__main__':
    main()
