import psycopg2

conn = psycopg2.connect('host=localhost port=5433 dbname=my3_db user=postgres password=postgres')
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
tables = cur.fetchall()
print('✅ Database tables created successfully:')
for t in tables:
    print(f'  - {t[0]}')
conn.close()



