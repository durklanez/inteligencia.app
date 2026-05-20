from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
import requests

app = Flask(__name__)
CORS(app)

# =========================
# CRIAR BANCO
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

        username = data.get("username")
        password = data.get("password")

        if not username or not password:

            return jsonify({
                "msg": "Preencha tudo"
            })

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "msg": "Conta criada com sucesso"
        })

    except sqlite3.IntegrityError:

        return jsonify({
            "msg": "Usuário já existe"
        })

    except Exception as e:

        print("ERRO REGISTER:", e)

        return jsonify({
            "msg": str(e)
        })

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

            return jsonify({
                "msg": "Login OK"
            })

        else:

            return jsonify({
                "msg": "Credenciais inválidas"
            })

    except Exception as e:

        print("ERRO LOGIN:", e)

        return jsonify({
            "msg": str(e)
        })

# =========================
# CHAT IA GROQ
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        mensagem = data.get("mensagem")

        resposta = requests.post(

            "https://api.groq.com/openai/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },

            json={

                "model": "llama3-70b-8192",

                "messages": [

                    {
                        "role": "system",
                        "content": """
Você é uma IA programadora avançada.
Ajude com:
Python
HTML
CSS
JavaScript
Flask
Banco de dados
APIs
Apps
Sites
Bots
                """
                    },

                    {
                        "role": "user",
                        "content": mensagem
                    }

                ]

            }

        )

        resultado = resposta.json()

        print(resultado)

        texto = resultado["choices"][0]["message"]["content"]

        return jsonify({
            "resposta": texto
        })

    except Exception as e:

        print("ERRO IA:", e)

        return jsonify({
            "resposta": "Erro na IA"
        })

# =========================
# START
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
