from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# API KEY
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
# REGISTER (CORRIGIDO)
# =========================
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"msg": "Preencha tudo"})

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        print("✅ Usuário criado:", username)

        return jsonify({"msg": "Conta criada com sucesso"})

    except sqlite3.IntegrityError:
        return jsonify({"msg": "Usuário já existe"})

    except Exception as e:
        print("❌ ERRO REGISTER:", e)
        return jsonify({"msg": "Erro no servidor"})

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
        print("❌ ERRO LOGIN:", e)
        return jsonify({"msg": "Erro no login"})

# =========================
# IA
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
Você é uma IA tipo Replit.

- Sempre responde completo
- Se pedir código → envia código completo
- Usa ``` para código
"""
                },
                {"role": "user", "content": mensagem}
            ]
        )

        return jsonify({
            "resposta": resposta.choices[0].message.content
        })

    except Exception as e:
        print("❌ ERRO IA:", e)
        return jsonify({"resposta": "Erro na IA"})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
