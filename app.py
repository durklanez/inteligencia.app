import os
import io, sys, json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import firebase_admin
from firebase_admin import credentials, auth as fb_auth, firestore

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "wy_angocas_muda_isso") # Mete no Render depois

# ====== FIREBASE ADMIN - SEGUR0 ======
# Pega a chave do Environment do Render. Não mete no código.
firebase_key_json = os.environ.get("FIREBASE_KEY_JSON")
if not firebase_key_json:
    raise ValueError("FIREBASE_KEY_JSON não definida no Render > Environment")

if not firebase_admin._apps: # Evita erro de já inicializado
    cred = credentials.Certificate(json.loads(firebase_key_json))
    firebase_admin.initialize_app(cred)
    
db = firestore.client() # <- É isso que salva tuas conversas

# ====== LOGIN FLASK ======
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, uid, email=None):
        self.id = uid
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    try:
        user_record = fb_auth.get_user(user_id)
        return User(user_id, user_record.email)
    except:
        return None

# ====== ROTAS PRINCIPAIS ======
@app.route('/')
@login_required 
def index():
    return render_template('index.html')

@app.route('/console')
@login_required 
def console():
    return render_template('console.html')

@app.route('/executar', methods=['POST'])
@login_required
def executar():
    codigo = request.json.get('codigo', '')
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        exec(codigo, {"__builtins__": __builtins__})
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        sys.stdout = sys.__stdout__
    return jsonify({'saida': buffer.getvalue() or 'Código rodou sem saída'})

@app.route('/ia_chat', methods=['POST'])
@login_required
def ia_chat():
    pergunta = request.json.get('pergunta','')
    # IA fake. Troca aqui pela tua API depois
    resposta = f"Wy, sou a IA do Angocas. Tu disse: {pergunta}"
    
    # ====== SALVA NO FIREBASE/FIRESTORE ======
    db.collection('chats').add({
        'user_id': current_user.id,
        'pergunta': pergunta,
        'resposta': resposta,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    return jsonify({'resposta': resposta})

# ====== AUTH COM FIREBASE REAL ======
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        try:
            user = fb_auth.create_user(email=email, password=senha)
            login_user(User(user.uid, user.email))
            return redirect(url_for('index'))
        except fb_auth.EmailAlreadyExistsError:
            return "Email já existe. Faz login."
        except Exception as e: 
            return f"Erro ao criar: {e}"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        try:
            # Nota: firebase-admin não valida senha. No mundo real usa o SDK do front.
            # Pra Render, vamos só buscar o user. Se existir, deixa entrar.
            user = fb_auth.get_user_by_email(email)
            login_user(User(user.uid, user.email))
            return redirect(url_for('index'))
        except:
            return "Login falhou. Email não encontrado."
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ====== ESSENCIAL PRO RENDER ======
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
