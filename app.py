import os
import json
from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# ========== CONFIG FIREBASE PARA RENDER ==========
# Pega a chave secreta que tu vai colar no Render > Environment
firebase_key_str = os.getenv("FIREBASE_KEY")

if not firebase_key_str:
    raise ValueError("ERRO FATAL: A variável FIREBASE_KEY não foi encontrada no Render. Vai em Settings > Environment e cria ela.")

# Transforma o texto em dicionário e inicia o Firebase
try:
    cred_dict = json.loads(firebase_key_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase conectado 100%")
except json.JSONDecodeError:
    raise ValueError("ERRO: O conteúdo da FIREBASE_KEY não é um JSON válido. Cola o ficheiro .json inteiro lá.")
# =================================================

@app.route("/")
def home():
    return jsonify({"status": "API no ar wy 🚀", "firebase": "OK"})

@app.route("/teste-firestore")
def teste_firestore():
    # Essa rota só pra testar se conectou no banco
    try:
        db.collection("teste_render").document("ok").set({"funcionou": True, "data": "2026-07-03"})
        return jsonify({"db": "Conectado no Firestore. Deu certo!"})
    except Exception as e:
        return jsonify({"erro_db": str(e)}), 500

if __name__ == "__main__":
    # Render usa a porta que ele te dá
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
