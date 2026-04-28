from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# IA (OpenAI)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# =========================
# BANCO
# =========================
def criar_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

criar_db()

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
    except:
        return jsonify({"msg": "Usuário já existe"})

    conn.close()
    return jsonify({"msg": "Conta criada com sucesso"})

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({"msg": "Login OK"})
    else:
        return jsonify({"msg": "Credenciais inválidas"})

# =========================
# IA REAL
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensagem = data.get("mensagem")

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em programação, cria apps, jogos e corrige código."},
                {"role": "user", "content": mensagem}
            ]
        )

        texto = resposta.choices[0].message.content

        return jsonify({"resposta": texto})

    except Exception as e:
        print("ERRO IA:", e)
        return jsonify({"resposta": "Erro ao conectar com IA"})

# =========================
# RODAR
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
