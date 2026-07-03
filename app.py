import os
import json
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# ========== FIREBASE VIA VARIÁVEL DE AMBIENTE ==========
# 1. Pega a chave secreta que tu colocou no Render
firebase_key_json = os.environ.get('FIREBASE_KEY')

if not firebase_key_json:
    raise ValueError("ERRO: FIREBASE_KEY não foi definida no Render. Vai em Settings > Environment")

# 2. Transforma o texto gigante em dicionário e inicia
cred = credentials.Certificate(json.loads(firebase_key_json))
firebase_admin.initialize_app(cred)
db = firestore.client()
# =======================================================

@app.route("/")
def home():
    return jsonify({"status": "API no ar wy 🚀", "firebase": "Conectado"})

@app.route("/teste")
def teste_db():
    # Rota pra testar se conectou no Firestore
    try:
        doc_ref = db.collection('teste').document('ok')
        doc_ref.set({'funcionou': True})
        return jsonify({"db": "Conectado no Firestore 100%"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
