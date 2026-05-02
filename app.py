from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# =========================
# API KEY
# =========================
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("❌ API KEY NÃO ENCONTRADA")
else:
    print("✅ API KEY OK")

client = OpenAI(api_key=api_key)

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
    try:
        data = request.get_json()

        if not data:
            return jsonify({"msg": "Sem dados"})

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

        print("✅ Criado:", username)

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

        if not data or "mensagem" not in data:
            return jsonify({"resposta": "Sem mensagem"})

        mensagem = data.get("mensagem")

        print("📩:", mensagem)

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é uma IA que ajuda a programar e gerar código."
                },
                {
                    "role": "user",
                    "content": mensagem
                }
            ]
        )

        texto = resposta.choices[0].message.content

        print("🤖:", texto)

        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ ERRO IA:", e)

        return jsonify({
            "resposta": f"Erro: {str(e)}"
        })

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
