from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os

app = Flask(__name__)
app.secret_key = 'pp2amiguinhos'  # para controlar sessões
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# IA
model = tf.keras.models.load_model("dataset.ipynb")
classes = ['COVID', 'Lung_Opacity', 'Normal', 'Viral Pneumonia']

# Função para conectar ao banco
def conectar():
    return sqlite3.connect('login.db')

# ---------- ROTAS ----------

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
            conn.commit()
            msg = "Usuário cadastrado com sucesso!"
            return render_template('login.html', msg=msg)
        except:
            msg = "Erro: e-mail já cadastrado!"
            return render_template('cadastro.html', msg=msg)
        finally:
            conn.close()
    return render_template('cadastro.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        session['usuario'] = usuario[1]
        return redirect(url_for('site'))
    else:
        return render_template('login.html', msg="E-mail ou senha incorretos")

@app.route('/site')
def site():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    return render_template('site.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------- UPLOAD E ANÁLISE ----------

@app.route('/analisar', methods=['POST'])
def analisar():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    arquivo = request.files['imagem']
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], arquivo.filename)
    arquivo.save(caminho)

    img = image.load_img(caminho, target_size=(224, 224))
    img_array = np.expand_dims(image.img_to_array(img) / 255.0, axis=0)

    pred = model.predict(img_array)[0]
    idx = np.argmax(pred)
    resultado = classes[idx]
    confianca = round(float(pred[idx]) * 100, 2)

    return render_template('resultado.html',
                           imagem=arquivo.filename,
                           resultado=resultado,
                           confianca=confianca,
                           usuario=session['usuario'])

if __name__ == '__main__':
    app.run(debug=True) 

