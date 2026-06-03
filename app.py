from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests

import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# =========================
# FIREBASE INIT
# =========================

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")

# =========================
# REGISTER (FIRESTORE)
# =========================

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(force=True)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"msg": "Preencha tudo"})

        # verificar se já existe
        users_ref = db.collection("users")
        query = users_ref.where("username", "==", username).stream()

        for _ in query:
            return jsonify({"msg": "Usuário já existe"})

        # criar user
        users_ref.add({
            "username": username,
            "password": password
        })

        return jsonify({"msg": "Conta criada com sucesso"})

    except Exception as e:
        print(e)
        return jsonify({"msg": "Erro no register"})

# =========================
# LOGIN (FIRESTORE)
# =========================

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)

        username = data.get("username")
        password = data.get("password")

        users_ref = db.collection("users")

        query = users_ref.where("username", "==", username)\
                          .where("password", "==", password)\
                          .stream()

        user_found = False

        for _ in query:
            user_found = True
            break

        if user_found:
            return jsonify({"msg": "Login OK"})
        else:
            return jsonify({"msg": "Credenciais inválidas"})

    except Exception as e:
        print(e)
        return jsonify({"msg": "Erro no login"})

# =========================
# CHAT IA (GROQ)
# =========================

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        mensagem = data.get("mensagem")

        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            return jsonify({"resposta": "GROQ_API_KEY não encontrada"})

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é uma IA inteligente e ajuda programadores."
                    },
                    {
                        "role": "user",
                        "content": mensagem
                    }
                ]
            }
        )

        resultado = response.json()
        texto = resultado["choices"][0]["message"]["content"]

        return jsonify({"resposta": texto})

    except Exception as e:
        print("ERRO IA:", e)
        return jsonify({"resposta": "Erro na IA"})

# =========================
# START
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
