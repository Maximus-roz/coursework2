import psycopg2
from config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("SHOW client_encoding;")
print("client_encoding:", cur.fetchone())
cur.execute("SHOW lc_messages;")
print("lc_messages:", cur.fetchone())
cur.execute("SELECT count(*) FROM countries;")
print("countries:", cur.fetchone())
cur.execute("SELECT count(*) FROM aeroplanes;")
print("aeroplanes:", cur.fetchone())
cur.close(); conn.close()
