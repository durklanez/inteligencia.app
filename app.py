from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import os
import requests

import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# =========================
# FIREBASE INIT (MANTIDO)
# =========================
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "projectId": "angocas-8b3e3"
})
db = firestore.client()

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# REGISTER - ACEITA HTML E API
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    # 1. GET = Mostra a tela HTML
    if request.method == "GET":
        return render_template("register.html")
    
    # 2. POST = Recebe dados do form HTML OU da API
    try:
        # Detecta se veio JSON da API ou Form do HTML
        if request.is_json:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            is_api = True
        else:
            username = request.form.get("usuario")
            password = request.form.get("senha")
            is_api = False

        if not username or not password:
            msg = {"msg": "Preencha tudo"}
            return jsonify(msg) if is_api else render_template("register.html", erro="Preencha tudo")

        users_ref = db.collection("users")
        query = users_ref.where("username", "==", username).stream()

        for _ in query:
            msg = {"msg": "Usuário já existe"}
            return jsonify(msg) if is_api else render_template("register.html", erro="Usuário já existe")

        users_ref.add({
            "username": username,
            "password": password
        })

        msg = {"msg": "Conta criada com sucesso"}
        return jsonify(msg) if is_api else redirect(url_for("login"))

    except Exception as e:
        print("REGISTER ERROR:", e)
        msg = {"msg": "Erro no register"}
        return jsonify(msg), 500 if is_api else render_template("register.html", erro="Erro no servidor")

# =========================
# LOGIN - ACEITA HTML E API
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    # 1. GET = Mostra a tela HTML
    if request.method == "GET":
        return render_template("login.html")
    
    # 2. POST = Recebe dados do form HTML OU da API
    try:
        if request.is_json:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            is_api = True
        else:
            username = request.form.get("usuario")
            password = request.form.get("senha")
            is_api = False

        users_ref = db.collection("users")
        query = users_ref.where("username", "==", username)\
                          .where("password", "==", password)\
                          .stream()

        for _ in query:
            msg = {"msg": "Login OK"}
            return jsonify(msg) if is_api else redirect(url_for("dashboard")) # manda pra dashboard depois

        msg = {"msg": "Credenciais inválidas"}
        return jsonify(msg) if is_api else render_template("login.html", erro="Credenciais inválidas")

    except Exception as e:
        print("LOGIN ERROR:", e)
        msg = {"msg": "Erro no login"}
        return jsonify(msg), 500 if is_api else render_template("login.html", erro="Erro no servidor")

# =========================
#
