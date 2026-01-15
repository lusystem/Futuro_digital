import psycopg2
import sys

try:
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='123', host='localhost', port=5432)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='gestao_testes'")
    if cur.fetchone():
        print('Database gestao_testes already exists')
    else:
        cur.execute('CREATE DATABASE gestao_testes')
        print('Database gestao_testes created')
    cur.close()
    conn.close()
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
