from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import os
import requests
import subprocess, sys, tempfile

# Firebase
import firebase_admin
from firebase_admin import credentials, auth

# =========================
# CONFIG
# =========================
app = Flask(__name__)
CORS(app)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_Cola_Sua_Chave_Aqui")

# Firebase - Pega a key do Secret File do Render
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# =========================
# ROTAS PÁGINAS HTML
# =========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html") # O MENU

@app.route("/chat_ui")
def chat_ui():
    return render_template("chat.html") # O CONSOLE

# =========================
# ROTAS API AUTH FIREBASE
# =========================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    try:
        user = auth.create_user(email=data["email"], password=data["password"])
        return jsonify({"status": "ok", "uid": user.uid})
    except auth.EmailAlreadyExistsError:
        return jsonify({"status": "error", "msg": "A conta já existe"}), 400
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 400

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        # Firebase não valida senha no backend sem SDK Admin. Só checa se existe.
        user = auth.get_user_by_email(data["email"])
        return jsonify({"status": "ok", "uid": user.uid})
    except Exception:
        return jsonify({"status": "error", "msg": "Email ou senha inválidos"}), 400

# =========================
# ROTA IA GROQ
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("mensagem", "")
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": msg}]}
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
    resposta = r.json()["choices"][0]["message"]["content"]
    return jsonify({"resposta": resposta})

# =========================
# ROTA RUN - EXECUTAR CODIGO
# =========================
@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    code = data.get("code", "")

    # Bloqueio basico de comandos perigosos
    bloqueados = ["import os", "import sys", "subprocess", "open(", "__import__"]
    if any(b in code for b in bloqueados):
        return jsonify({"output": "Erro: Comando bloqueado por segurança."})

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run([sys.executable, tmp_path], capture_output=True, text=True, timeout=5)
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        output = "Erro: Timeout 5s. Loop infinito?"
    except Exception as e:
        output = f"Erro: {e}"
    finally:
        os.remove(tmp_path)
    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
