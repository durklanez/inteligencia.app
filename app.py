from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# APP SETUP
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# FIREBASE SETUP
# =========================
# Usa variável de ambiente ou ficheiro local
FIREBASE_PATH = os.getenv("FIREBASE_PATH", "firebase.json")

cred = credentials.Certificate(FIREBASE_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

# =========================
# GROQ IA SETUP
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Preencha usuário e senha"}), 400

    # verificar se user existe
    existing = db.collection("users").where("username", "==", username).stream()
    if any(existing):
        return jsonify({"msg": "Usuário já existe"}), 409

    hashed_password = generate_password_hash(password)

    db.collection("users").add({
        "username": username,
        "password": hashed_password
    })

    return jsonify({"msg": "Conta criada com sucesso"}), 201


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Preencha usuário e senha"}), 400

    users = db.collection("users").where("username", "==", username).stream()

    user_doc = None
    for u in users:
        user_doc = u.to_dict()
        break

    if not user_doc:
        return jsonify({"msg": "Usuário não existe"}), 404

    if not check_password_hash(user_doc["password"], password):
        return jsonify({"msg": "Senha incorreta"}), 401

    return jsonify({
        "msg": "Login realizado com sucesso",
        "username": username
    }), 200


# =========================
# CHAT IA (GROQ)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message")
    username = data.get("username")

    if not user_msg:
        return jsonify({"msg": "Mensagem vazia"}), 400

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Tu és uma IA inteligente, útil e direta."},
            {"role": "user", "content": user_msg}
        ]
    }

    response = requests.post(GROQ_URL, json=payload, headers=headers)

    if response.status_code != 200:
        return jsonify({
            "msg": "Erro na IA",
            "error": response.text
        }), 500

    result = response.json()
    answer = result["choices"][0]["message"]["content"]

    # guardar histórico (opcional mas útil)
    if username:
        db.collection("chats").add({
            "username": username,
            "message": user_msg,
            "response": answer
        })

    return jsonify({
        "response": answer
    }), 200


# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return jsonify({"msg": "Intelligence App API online"}), 200


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
