from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    firebase_key = os.environ.get("FIREBASE_KEY")
    cred_dict = json.loads(firebase_key)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except:
    db = None
    print("Firebase sem key")

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/teste-firestore', methods=['POST', 'OPTIONS'])
def teste_firestore():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    pergunta = data.get('pergunta', '')
    historico = data.get('historico', [])

    try:
        mensagens = [{"role": "system", "content": "Você é a Eli AI. Responde em pt-br curta."}] + historico + [{"role": "user", "content": pergunta}]
        chat_completion = client.chat.completions.create(messages=mensagens, model="llama-3.1-8b-instant")
        texto_eli = chat_completion.choices[0].message.content
    except Exception as e:
        texto_eli = f"Erro Groq: {str(e)}"

    codigo = ""
    tipo = "js"
    if "```" in texto_eli:
        partes = texto_eli.split("```")
        if len(partes) > 1:
            codigo = partes[1].strip()

    if db:
        db.collection("chats").add({"pergunta": pergunta, "resposta": texto_eli})
    
    return jsonify({"resposta": texto_eli, "codigo": codigo, "tipo": tipo})
