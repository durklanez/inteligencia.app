import os
import json
from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError

app = Flask(__name__)

# ===== INICIALIZAR FIREBASE VIA SECRET FILE DO RENDER =====
try:
    SECRET_FILE_PATH = '/etc/secrets/firebase-adminsdk.json'
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(SECRET_FILE_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin inicializado com sucesso via Secret File")
except Exception as e:
    print(f"ERRO CRÍTICO AO INICIAR FIREBASE: {e}")
    
# ===== HTML CRIAR CONTA =====
REGISTER_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Criar Conta</title>
<style>
body { font-family: Arial; background: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
.box { background: #1e293b; padding: 30px; border-radius: 12px; width: 320px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
input, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: none; font-size: 15px; }
input { background: #334155; color: #fff; outline: none; }
button { background: #3b82f6; color: #fff; font-weight: bold; cursor: pointer; transition: 0.2s; }
button:hover { background: #2563eb; }
#msg { margin-top: 10px; font-size: 14px; text-align: center; min-height: 20px; }
a { color: #60a5fa; text-decoration: none; }
</style>
</head>
<body>
<div class="box">
<h2>Criar Conta</h2>
<input id="email" type="email" placeholder="Email">
<input id="senha" type="password" placeholder="Senha min 6 chars">
<button onclick="registrar()">Criar Conta</button>
<p id="msg"></p>
<p>Já tem conta? <a href="/login">Fazer Login</a></p>
</div>
<script>
async function registrar() {
  const email = document.getElementById('email').value;
  const senha = document.getElementById('senha').value;
  const msg = document.getElementById('msg');
  msg.textContent = 'Aguarde...';
  msg.style.color = '#fbbf24';
  const res = await fetch('/api/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, senha})
  });
  const data = await res.json();
  msg.textContent = data.mensagem || data.erro;
  msg.style.color = res.ok ? '#4ade80' : '#f87171';
  if(res.ok) setTimeout(() => window.location.href = '/login', 1500);
}
</script>
</body>
</html>
"""

# ===== HTML LOGIN - AGORA COM MSG PRA MOSTRAR ERRO =====
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login</title>
<style>
body { font-family: Arial; background: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
.box { background: #1e293b; padding: 30px; border-radius: 12px; width: 320px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
input, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: none; font-size: 15px; }
input { background: #334155; color: #fff; outline: none; }
button { background: #10b981; color: #fff; font-weight: bold; cursor: pointer; transition: 0.2s; }
button:hover { background: #059669; }
#msg { margin-top: 10px; font-size: 14px; text-align: center; min-height: 20px; }
a { color: #60a5fa; text-decoration: none; }
</style>
</head>
<body>
<div class="box">
<h2>Login</h2>
<input id="email" type="email" placeholder="Email">
<input id="senha" type="password" placeholder="Senha">
<button onclick="logar()">Entrar</button>
<p id="msg"></p> <!-- ESSA LINHA FAZ APARECER O ERRO -->
<p>Não tem conta? <a href="/register">Criar Conta</a></p>
</div>
<script>
async function logar() {
  const email = document.getElementById('email').value;
  const senha = document.getElementById('senha').value;
  const msg = document.getElementById('msg');
  msg.textContent = 'Aguarde...';
  msg.style.color = '#fbbf24';
  const res = await fetch('/api/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, senha})
  });
  const data = await res.json();
  msg.textContent = data.mensagem || data.erro;
  msg.style.color = res.ok ? '#4ade80' : '#f87171';
}
</script>
</body>
</html>
"""

# ===== ROTAS =====
@app.route('/')
def home():
    return "<h1>API OK</h1><a href='/register'>Registrar</a> | <a href='/login'>Login</a>"

@app.route('/register')
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route('/login')
def login_page():
    return render_template_string(LOGIN_HTML)

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        if not email or not senha or len(senha) < 6:
            return jsonify({"erro": "Email e senha min 6 chars"}), 400
        
        user = auth.create_user(email=email, password=senha)
        return jsonify({"mensagem": "Conta criada com sucesso!", "ok": True})
    except auth.EmailAlreadyExistsError:
        return jsonify({"erro": "Este email já está em uso"}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        if not email or not senha:
            return jsonify({"erro": "Preencha email e senha"}), 400

        # ATENÇÃO: Firebase Admin não valida senha. Só checa se o email existe.
        # Pra validar senha de verdade, teria que usar Firebase Web SDK no front.
        user = auth.get_user_by_email(email)
        return jsonify({"mensagem": f"Bem-vindo, {user.email}", "ok": True})
    except auth.UserNotFoundError:
        return jsonify({"erro": "Email ou senha inválidos"}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
