import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

query_user = "SELECT * FROM usuario WHERE email LIKE '%%consultoria.farma.4y2%%'"
user_df = pd.read_sql_query(query_user, engine)

if not user_df.empty:
    user_id = user_df.iloc[0]['id']
    query_votes = f"""
    SELECT p.equipo_a, p.equipo_b, v.voto_ganador, v.goles_a_prediccion, v.goles_b_prediccion, v.voto_amarilla, v.voto_roja, v.fecha_voto 
    FROM voto v 
    JOIN partido p ON v.partido_id = p.id 
    WHERE v.usuario_id = {user_id}
    """
    votes_df = pd.read_sql_query(query_votes, engine)
    
    print("=== ANÁLISIS DE VOTOS ===")
    print(f"Total de partidos apostados: {len(votes_df)}")
    
    ganador_counts = votes_df['voto_ganador'].value_counts()
    print("\nTendencia de Voto Ganador:")
    for k, v in ganador_counts.items():
        print(f"  {k}: {v}")
        
    votes_df['resultado_exacto'] = votes_df['goles_a_prediccion'].astype(str) + " - " + votes_df['goles_b_prediccion'].astype(str)
    resultados_comunes = votes_df['resultado_exacto'].value_counts()
    print("\nResultados más comunes (Goles):")
    for k, v in resultados_comunes.head(5).items():
        print(f"  {k}: {v} veces")
        
    amarilla_counts = votes_df['voto_amarilla'].value_counts()
    print("\nVotos Tarjeta Amarilla:")
    for k, v in amarilla_counts.items():
        print(f"  {k}: {v}")
        
    roja_counts = votes_df['voto_roja'].value_counts()
    print("\nVotos Tarjeta Roja:")
    for k, v in roja_counts.items():
        print(f"  {k}: {v}")
        
    goles_a_promedio = votes_df['goles_a_prediccion'].mean()
    goles_b_promedio = votes_df['goles_b_prediccion'].mean()
    print("\nPromedio de goles predichos:")
    print(f"  Equipo Local (A): {goles_a_promedio:.2f}")
    print(f"  Equipo Visitante (B): {goles_b_promedio:.2f}")
    
else:
    print("User not found.")
