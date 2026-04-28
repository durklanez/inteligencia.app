from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
    return jsonify({"msg": "Credenciais inválidas"})

# =========================
# IA REPLIT STYLE
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensagem = data.get("mensagem")

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Você é uma IA tipo Replit Ghostwriter.

REGRAS:
- Sempre explica
- Se o usuário pedir código:
  → retorna código COMPLETO
  → usa ``` para marcar código
- Código deve funcionar
- Seja direto e profissional
"""
                },
                {"role": "user", "content": mensagem}
            ]
        )

        return jsonify({
            "resposta": resposta.choices[0].message.content
        })

    except Exception as e:
        print(e)
        return jsonify({"resposta": "Erro na IA"})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
