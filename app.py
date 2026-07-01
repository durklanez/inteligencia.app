import os
import firebase_admin
from firebase_admin import credentials, auth as fb_auth, firestore
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "wy_angocas_muda_isso_no_render")

# ====== FIREBASE ADMIN ======
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('/etc/secrets/serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase iniciado com sucesso")
except Exception as e:
    raise RuntimeError(f"Erro ao iniciar Firebase. Verifica Secret Files: {e}")

# ====== LOGIN FLASK ======
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

class User(UserMixin):
    def __init__(self, uid, email, nome):
        self.id = uid
        self.email = email
        self.nome = nome

@login_manager.user_loader
def load_user(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        data = doc.to_dict()
        return User(user_id, data.get("email"), data.get("nome"))
    return None

# ====== PAGINAS ======
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("chat_page"))
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/chat")
@login_required
def chat_page():
    return render_template("chat.html", nome=current_user.nome)

# ====== API - CORRIGIDA PRA NÃO DAR UNDEFINED ======
@app.post("/api/register")
def api_register():
    data = request.get_json() or {}
    email = data.get("email")
    senha = data.get("senha")
    nome = data.get("nome")

    if not email or not senha or not nome:
        return jsonify({"erro": "Preenche tudo wy"}), 400

    try:
        user = fb_auth.create_user(email=email, password=senha, display_name=nome)
        db.collection("users").document(user.uid).set({
            "email": email,
            "nome": nome,
            "senha_hash": generate_password_hash(senha) # Agora todo user novo tem isso
        })
        return jsonify({"ok": True, "msg": "Conta criada!"}), 201

    except fb_auth.EmailAlreadyExistsError:
        return jsonify({"erro": "Esse email já existe"}), 409
    except Exception as e:
        print("Erro register:", e)
        return jsonify({"erro": f"Erro no servidor: {str(e)}"}), 500 # Agora manda erro real

@app.post("/api/login")
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        return jsonify({"erro": "Preenche email e senha"}), 400

    try:
        user_ref = db.collection("users").where("email", "==", email).limit(1).get()
        if not user_ref:
            return jsonify({"erro": "Email ou senha errados"}), 401

        user_doc = user_ref[0]
        user_data = user_doc.to_dict()

        # CORREÇÃO DO UNDEFINED AQUI 👇
        senha_hash = user_data.get("senha_hash")
        if not senha_hash or not check_password_hash(senha_hash, senha):
            return jsonify({"erro": "Email ou senha errados"}), 401

        user = User(user_doc.id, user_data["email"], user_data["nome"])
        login_user(user)
        return jsonify({"ok": True}), 200

    except Exception as e:
        print("Erro login:", e)
        return jsonify({"erro": f"Erro no servidor: {str(e)}"}), 500 # Agora manda erro real

@app.post("/api/logout")
@login_required
def api_logout():
    logout_user()
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
