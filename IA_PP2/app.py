from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "chave-secreta-supersegura"  # Troque isso em produção!

# === Funções auxiliares ===
def get_db_connection():
    conn = sqlite3.connect("login.db")
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabela():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha_hash TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# === Rotas ===
@app.route('/')
def site():
    if "usuario" in session:
        return render_template('site.html', nome=session["usuario"])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = hash_senha(senha)

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE email = ? AND senha_hash = ?",
            (email, senha_hash)
        ).fetchone()
        conn.close()

        if user:
            session["usuario"] = user["nome"]
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('site'))
        else:
            flash("E-mail ou senha incorretos!", "danger")
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = hash_senha(senha)

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
                (nome, email, senha_hash)
            )
            conn.commit()
            conn.close()
            flash("Usuário cadastrado com sucesso!", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("E-mail já cadastrado!", "danger")
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.pop("usuario", None)
    flash("Logout realizado com sucesso!", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)
