import os
import firebase_admin
from firebase_admin import credentials, auth as fb_auth, firestore
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "muda_no_render")

# FIREBASE
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('/etc/secrets/serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase iniciado com sucesso")
except Exception as e:
    print(f"ERRO FIREBASE: {e}")

# LOGIN
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, uid, email, nome):
        self.id = uid
        self.email = email
        self.nome = nome

@login_manager.user_loader
def load_user(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        d = doc.to_dict()
        return User(user_id, d.get("email"), d.get("nome"))
    return None

# ROTAS PAGINA
@app.route("/")
def home():
    return redirect(url_for("chat_page")) if current_user.is_authenticated else redirect(url_for("register_page"))

@app.route("/register")
def register_page(): return render_template("register.html")

@app.route("/login")
def login_page(): return render_template("login.html")

@app.route("/chat")
@login_required
def chat_page(): return render_template("chat.html", nome=current_user.nome)

# ROTAS API
@app.post("/api/register")
def api_register():
    d = request.get_json(silent=True) or {} # silent=True pra não crashar
    email, senha = d.get("email"), d.get("senha")
    nome = d.get("nome") or "User"

    if not email or not senha:
        return jsonify({"erro": "Preenche email e senha wy"}), 400
    try:
        user = fb_auth.create_user(email=email, password=senha, display_name=nome)
        db.collection("users").document(user.uid).set({
            "email": email, "nome": nome, "senha_hash": generate_password_hash(senha)
        })
        return jsonify({"ok": True, "msg": "Conta criada!"}), 201
    except fb_auth.EmailAlreadyExistsError:
        return jsonify({"erro": "Email já existe"}), 409
    except Exception as e:
        print("Erro register:", e)
        return jsonify({"erro": "Erro no servidor"}), 500

@app.post("/api/login")
def api_login():
    d = request.get_json(silent=True) or {}
    email, senha = d.get("email"), d.get("senha")
    if not email or not senha:
        return jsonify({"erro": "Preenche tudo"}), 400
    try:
        res = db.collection("users").where("email", "==", email).limit(1).get()
        if not res: return jsonify({"erro": "Email ou senha
