import os # <- ESSENCIAL pro Render
import io, sys, json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyrebase

app = Flask(__name__)
app.secret_key = "wy_angocas_2026_muda_isso_depois"

# ====== CONFIG FIREBASE - COLA AS TUAS CHAVES AQUI ======
config = {
  "apiKey": "COLA_TUA_APIKEY_AQUI",
  "authDomain": "COLA_TU_PROJECT.firebaseapp.com",
  "projectId": "COLA_TU_PROJECT",
  "storageBucket": "COLA_TU_PROJECT.appspot.com",
  "messagingSenderId": "123",
  "appId": "1:123:web:abc",
  "databaseURL": ""
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# ====== LOGIN FLASK ======
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id): self.id = id

@login_manager.user_loader
def load_user(user_id): return User(user_id)

# ====== ROTAS PRINCIPAIS ======
@app.route('/')
@login_required 
def index():
    return render_template('index.html')

@app.route('/novos_app')
@login_required
def novos_app():
    return render_template('novos_app.html')

@app.route('/console')
@login_required 
def console():
    lang = request.args.get('lang', 'python')
    return render_template('console.html', lang=lang)

@app.route('/executar', methods=['POST'])
@login_required
def executar():
    codigo = request.json.get('codigo', '')
    try:
        buffer = io.StringIO()
        sys.stdout = buffer
        exec(codigo, {}) # CUIDADO: só pra teste teu
        sys.stdout = sys.__stdout__
        saida = buffer.getvalue()
        return jsonify({'saida': saida if saida else 'Código rodou sem saída'})
    except Exception as e:
        sys.stdout = sys.__stdout__
        return jsonify({'saida': f'Erro: {str(e)}'})

@app.route('/ia_chat', methods=['POST'])
@login_required
def ia_chat():
    pergunta = request.json.get('pergunta','')
    
    # ====== IA FAKE POR ENQUANTO ======
    if "codigo" in pergunta.lower() or "python" in pergunta.lower():
        resposta = f"Feito wy. Cola isso:\n```python\n# {pergunta}\nprint('Hello from IA Angocas')\nfor i in range(3):\n  print(i)\n```"
    else:
        resposta = f"Wy, sou a IA do Angocas. Pede código Python que eu mando. Tu disse: {pergunta}"
    
    return jsonify({'resposta': resposta})

# ====== AUTH ======
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email'); senha = request.form.get('senha')
        try:
            auth.create_user_with_email_and_password(email, senha)
            return redirect(url_for('login'))
        except: return "Erro ao criar conta. Email já existe?"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email'); senha = request.form.get('senha')
        try:
            user = auth.sign_in_with_email_and_password(email, senha)
            login_user(User(user['localId']))
            return redirect(url_for('index'))
        except: return "Login falhou. Email ou senha errados."
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('login'))

# ====== ESSENCIAL PRO RENDER ======
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) # Pega a porta do Render, se não tiver usa 5000
    app.run(host='0.0.0.0', port=port, debug=False) # debug=False no Render
