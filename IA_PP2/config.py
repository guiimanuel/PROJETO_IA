import sqlite3

conn = sqlite3.connect('login.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")
