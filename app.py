from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# =========================
# FIREBASE
# =========================
FIREBASE_PATH = os.getenv("FIREBASE_PATH", "firebase.json")

cred = credentials.Certificate(FIREBASE_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

# =========================
# GROQ
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

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

    if not username or not password:
        return jsonify({"msg": "Preencha usuário e senha"}), 400

    users = db.collection("users").where("username", "==", username).stream()

    if any(users):
        return jsonify({"msg": "Usuário já existe"}), 409

    db.collection("users").add({
        "username": username,
        "password": generate_password_hash(password)
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

    user_data = None

    for user in users:
        user_data = user.to_dict()
        break

    if not user_data:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    if not check_password_hash(user_data["password"], password):
        return jsonify({"msg": "Senha incorreta"}), 401

    return jsonify({
        "msg": "Login realizado com sucesso",
        "username": username
    }), 200

# =========================
# CHAT IA
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    message = data.get("message")
    username = data.get("username", "Anônimo")

    if not message:
        return jsonify({"msg": "Mensagem vazia"}), 400

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "Você é uma IA inteligente, útil e amigável."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    response = requests.post(
        GROQ_URL,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return jsonify({
            "msg": "Erro na IA",
            "erro": response.text
        }), 500

    result = response.json()
    answer = result["choices"][0]["message"]["content"]

    db.collection("chats").add({
        "username": username,
        "message": message,
        "response": answer
    })

    return jsonify({
        "response": answer
    }), 200

# =========================
# HISTÓRICO
# =========================
@app.route("/history/<username>", methods=["GET"])
def history(username):
    chats = db.collection("chats").where(
        "username", "==", username
    ).stream()

    history = []

    for chat in chats:
        history.append(chat.to_dict())

    return jsonify(history)

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
