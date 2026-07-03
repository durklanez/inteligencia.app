from flask import Flask, render_template, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import firebase_admin
from firebase_admin import credentials, auth
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# ===== BLOCO FIREBASE ADMIN - SEM FICHEIRO .JSON =====
# Ele vai ler direto da variável de ambiente do Render
firebase_key_json = os.environ.get('FIREBASE_KEY_JSON')

if not firebase_key_json:
    raise ValueError("FATAL: Variável de ambiente FIREBASE_KEY_JSON não foi encontrada.")

try:
    cred_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK iniciado com sucesso!")
except json.JSONDecodeError:
    raise ValueError("FATAL: O conteúdo de FIREBASE_KEY_JSON não é um JSON válido. Verifica as quebras de linha.")
# =====================================================

# ===== GOOGLE OAUTH LOGIN =====
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
# ==============================


@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)


@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/callback')
def callback():
    token = google.authorize_access_token()
    id_token = token.get('id_token')
    
    if not id_token:
        return "Erro: ID Token não recebido.", 400

    # Verifica o token com o Firebase Admin
    decoded_token = auth.verify_id_token(id_token)
    
    session['user'] = {
        'uid': decoded_token['uid'],
        'name': decoded_token.get('name'),
        'email': decoded_token.get('email'),
        'picture': decoded_token.get('picture')
    }
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', user=session['user'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
