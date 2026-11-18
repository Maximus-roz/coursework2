import psycopg2
from src.config import DB_CONFIG

print("DB_CONFIG:", {k: v for k, v in DB_CONFIG.items() if k != "password"})

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("SHOW server_encoding;")
print("server_encoding:", cur.fetchone())

cur.execute("SHOW client_encoding;")
print("client_encoding:", cur.fetchone())

cur.execute("SELECT country_id, name FROM countries;")
print("countries:", cur.fetchall())

cur.execute("SELECT aeroplane_id, callsign, origin_country FROM aeroplanes LIMIT 5;")
print("aeroplanes:", cur.fetchall())

cur.close()
conn.close()