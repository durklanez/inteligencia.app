from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth
import firebase_admin
from firebase_admin import credentials, auth
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "uma-chave-super-secreta-muda-isso")

# ===== FIREBASE ADMIN SEM FICHEIRO =====
key_json = os.environ.get('FIREBASE_KEY_JSON')
if not key_json:
    raise ValueError("ERRO: Variável de ambiente FIREBASE_KEY_JSON não encontrada no Render.")

cred_dict = json.loads(key_json)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
print("✅ Firebase Admin iniciado com sucesso")
# ========================================

# ===== GOOGLE LOGIN OAUTH =====
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
    id_token = token['id_token']
    
    # Verifica o token no Firebase Admin
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
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/api/sessionLogin', methods=['POST'])
def sessionLogin():
    # Rota pra quando tu fizer login com JS no front
    id_token = request.json['idToken']
    decoded_token = auth.verify_id_token(id_token)
    session['user'] = {'uid': decoded_token['uid'], 'email': decoded_token.get('email')}
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
