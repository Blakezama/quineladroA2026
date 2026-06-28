import sqlite3
import pandas as pd

conn = sqlite3.connect('instance/mundial.db')

query_users = "SELECT id, nombre, email FROM usuario"
users_df = pd.read_sql_query(query_users, conn)
print("ALL USERS:")
pd.set_option('display.max_rows', None)
print(users_df)

conn.close()
