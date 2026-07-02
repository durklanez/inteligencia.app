import os
import requests
from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

# ===== CONFIG FIREBASE =====
API_KEY = "COLA_A_TUA_WEB_API_KEY_AQUI" # <--- ISSO É NOVO WY
SECRET_FILE_PATH = '/etc/secrets/firebase-adminsdk.json'

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(SECRET_FILE_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin iniciado com sucesso")
except Exception as e:
    print(f"ERRO FIREBASE: {e}")

# ===== HTML TELAS =====
REGISTER_HTML = """
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Criar Conta</title><style>
body{font-family:Arial;background:#0f172a;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#1e293b;padding:30px;border-radius:12px;width:320px}
input,button{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none;font-size:15px}
input{background:#334155;color:#fff}button{background:#3b82f6;color:#fff;font-weight:bold;cursor:pointer}
#msg{margin-top:10px;font-size:14px;text-align:center;min-height:20px}a{color:#60a5fa}</style></head><body>
<div class="box"><h2>Criar Conta</h2><input id="email" type="email" placeholder="Email">
<input id="senha" type="password" placeholder="Senha min 6">
<button onclick="registrar()">Criar Conta</button><p id="msg"></p>
<p>Já tem conta? <a href="/login">Fazer Login</a></p></div>
<script>
async function registrar(){const e=document.getElementById('email').value,s=document.getElementById('senha').value,m=document.getElementById('msg');
m.textContent='Aguarde...';m.style.color='#fbbf24';const r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,senha:s})});
const d=await r.json();m.textContent=d.mensagem||d.erro;m.style.color=r.ok?'#4ade80':'#f87171';if(r.ok)setTimeout(()=>location.href='/login',1500)}</script></body></html>
"""

LOGIN_HTML = """
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login</title><style>
body{font-family:Arial;background:#0f172a;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#1e293b;padding:30px;border-radius:12px;width:320px}
input,button{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none;font-size:15px}
input{background:#334155;color:#fff}button{background:#10b981;color:#fff;font-weight:bold;cursor:pointer}
#msg{margin-top:10px;font-size:14px;text-align:center;min-height:20px}a{color:#60a5fa}</style></head><body>
<div class="box"><h2>Login</h2><input id="email" type="email" placeholder="Email">
<input id="senha" type="password" placeholder="Senha">
<button onclick="logar()">Entrar</button><p id="msg"></p>
<p>Não tem conta? <a href="/register">Criar Conta</a></p></div>
<script>
async function logar(){const e=document.getElementById('email').value,s=document.getElementById('senha').value,m=document.getElementById('msg');
m.textContent='Aguarde...';m.style.color='#fbbf24';const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,senha:s})});
const d=await r.json();m.textContent=d.mensagem||d.erro;m.style.color=r.ok?'#4ade80':'#f87171'}</script></body></html>
"""

# ===== ROTAS =====
@app.route('/')
def home(): return "<a href='/register'>Registrar</a> | <a href='/login'>Login</a>"

@app.route('/register')
def register_page(): return render_template_string(REGISTER_HTML)

@app.route('/login')
def login_page(): return render_template_string(LOGIN_HTML)

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        email, senha = data.get('email'), data.get('senha')
        if not email or not senha or len(senha) < 6: return jsonify({"erro": "Email e senha min 6"}), 400
        auth.create_user(email=email, password=senha)
        return jsonify({"mensagem": "Conta criada!", "ok": True})
    except auth.EmailAlreadyExistsError: return jsonify({"erro": "Email já em uso"}), 400
    except Exception as e: return jsonify({"erro": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email, senha = data.get('email'), data.get('senha')
        if not email or not senha: return jsonify({"erro": "Preencha tudo"}), 400
        
        # LOGIN REAL VIA API REST DO FIREBASE
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        res = requests.post(url, json={"email": email, "password": senha, "returnSecureToken": True})
        
        if res.status_code == 200:
            return jsonify({"mensagem": "Login feito com sucesso!", "ok": True})
        else:
            erro = res.json().get('error', {}).get('message', 'Erro')
            if 'INVALID_PASSWORD' in erro or 'EMAIL_NOT_FOUND' in erro:
                return jsonify({"erro": "Email ou senha inválidos"}), 400
            return jsonify({"erro": erro}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
