import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troca_essa_chave_secreta_wy")

# ================= FIREBASE ADMIN = BACKEND = =================
FIREBASE_KEY_PATH = os.environ.get("FIREBASE_KEY_PATH", "sua_serviceAccountKey.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================= FIREBASE AUTH = LOGIN VIA API = =================
API_KEY = "AIzaSyDqKhBPZN6zQme8M-9o7xMYgUL4hnYsncY" # Tua Web API Key
REST_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
REST_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"

def firebase_signin(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(REST_AUTH_URL, json=payload)
    return r.json()

def firebase_signup(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(REST_SIGNUP_URL, json=payload)
    return r.json()

# ================= ROTAS =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        res = firebase_signin(email, password)
        
        if "idToken" in res:
            session["user"] = {"email": email, "uid": res["localId"], "idToken": res["idToken"]}
            flash("Login feito com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            error_msg = res.get("error", {}).get("message", "Erro desconhecido")
            if error_msg == "EMAIL_NOT_FOUND":
                flash("Email não encontrado. Cria conta primeiro.", "danger")
            elif error_msg == "INVALID_PASSWORD":
                flash("Senha errada wy.", "danger")
            elif error_msg == "OPERATION_NOT_ALLOWED":
                flash("Ativa o Email/senha no Firebase > Authentication.", "danger")
            else:
                flash(f"Erro: {error_msg}", "danger")
                
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        res = firebase_signup(email, password)
        
        if "idToken" in res:
            flash("Conta criada! Agora faz login.", "success")
            return redirect(url_for("login"))
        else:
            error_msg = res.get("error", {}).get("message", "Erro desconhecido")
            if error_msg == "EMAIL_EXISTS":
                flash("Esse email já existe wy.", "danger")
            elif error_msg == "WEAK_PASSWORD : Password should be at least 6 characters":
                flash("Senha fraca. Mete no mínimo 6 caracteres.", "danger")
            else:
                flash(f"Erro: {error_msg}", "danger")
                
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Saíste da conta.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
