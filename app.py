import os
import io, sys, json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import firebase_admin
from firebase_admin import credentials, auth as fb_auth, firestore

app = Flask(__name__)
app.secret_key = "wy_angocas_2026_muda_isso_depois"

# ====== FIREBASE ADMIN - A CHAVE SECRETA ======
# 1. Vai no Firebase > Configurações do Projeto > Contas de Serviço 
# 2. Gera nova chave privada > Baixa o JSON
# 3. Copia tudo e cola aqui entre as aspas triplas
firebase_key_json = """
{COLE_SEU_JSON_DO_FIREBASE_AQUI}
"""
cred = credentials.Certificate(json.loads(firebase_key_json))
firebase_admin.initialize_app(cred)
db = firestore.client() # <- É isso que salva as conversas

# ====== LOGIN FLASK ======
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id): self.id = id

@login_manager.user_loader
def load_user(user_id): return User(user_id)

# ====== ROTAS ======
@app.route('/')
@login_required 
def index(): return render_template('index.html')

@app.route('/console')
@login_required 
def console(): return render_template('console.html')

@app.route('/executar', methods=['POST'])
@login_required
def executar():
    codigo = request.json.get('codigo', '')
    try:
        buffer = io.StringIO()
        sys.stdout = buffer
        exec(codigo, {})
        sys.stdout = sys.__stdout__
        saida = buffer.getvalue()
        return jsonify({'saida': saida if saida else 'OK'})
    except Exception as e:
        sys.stdout = sys.__stdout__
        return jsonify({'saida': f'Erro: {str(e)}'})

@app.route('/ia_chat', methods=['POST'])
@login_required
def ia_chat():
    pergunta = request.json.get('pergunta','')
    resposta = f"Wy, sou a IA do Angocas. Tu disse: {pergunta}"
    
    # ====== SALVA NO FIREBASE AQUI ======
    db.collection('users').document(current_user.id).collection('chats').add({
        'pergunta': pergunta,
        'resposta': resposta
    })
    return jsonify({'resposta': resposta})

# ====== AUTH COM FIREBASE REAL ======
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email'); senha = request.form.get('senha')
        try:
            user = fb_auth.create_user(email=email, password=senha)
            login_user(User(user.uid))
            return redirect(url_for('index'))
        except Exception as e: return f"Erro: {e}"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email'); senha = request.form.get('senha')
        try:
            # Firebase-Admin não faz login com senha. Então a gente só verifica se existe
            user = fb_auth.get_user_by_email(email) 
            login_user(User(user.uid))
            return redirect(url_for('index'))
        except: return "Login falhou. Cria conta primeiro."
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
