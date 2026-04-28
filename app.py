from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# 🔑 API KEY
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("❌ API KEY NÃO ENCONTRADA!")
else:
    print("✅ API KEY CARREGADA!")

client = OpenAI(api_key=api_key)

# =========================
# DB
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
# TESTE
# =========================
@app.route("/teste")
def teste():
    return "Servidor OK 🚀"

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    try:
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

    except Exception as e:
        print("ERRO LOGIN:", e)
        return jsonify({"msg": "Erro no login"})

# =========================
# IA REAL
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensagem = data.get("mensagem")

        print("📩 Mensagem recebida:", mensagem)

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Você é uma IA tipo Replit.

REGRAS:
- Sempre explica
- Se pedir código → envia código completo
- Usa ``` para código
- Seja claro e profissional
"""
                },
                {"role": "user", "content": mensagem}
            ]
        )

        texto = resposta.choices[0].message.content

        print("🤖 Resposta IA:", texto)

        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ ERRO IA:", e)
        return jsonify({"resposta": "Erro ao conectar com IA"})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
