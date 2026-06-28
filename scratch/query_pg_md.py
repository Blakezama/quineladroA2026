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
    ORDER BY v.fecha_voto DESC
    """
    votes_df = pd.read_sql_query(query_votes, engine)
    print(votes_df.to_markdown(index=False))
else:
    print("User not found.")
