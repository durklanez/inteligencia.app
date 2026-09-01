from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/teste-firestore', methods=['POST', 'OPTIONS'])
def teste_firestore():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json() or {}
    pergunta = data.get('pergunta', '')
    historico = data.get('historico', [])

    # Carrega a chave diretamente na chamada para garantir a leitura do Render
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"resposta": "Erro: A variável GROQ_API_KEY não foi encontrada no Render.", "codigo": "", "tipo": "js"})

    try:
        client = Groq(api_key=api_key)
        mensagens = [{"role": "system", "content": "Você é a Eli AI. Responde em pt-br curta."}] + historico + [{"role": "user", "content": pergunta}]
        
        # Modelo atualizado e mais estável da Groq
        chat_completion = client.chat.completions.create(
            messages=mensagens, 
            model="llama-3.3-70b-versatile"
        )
        texto_eli = chat_completion.choices[0].message.content
    except Exception as e:
        texto_eli = f"Erro Groq: {str(e)}"

    codigo = ""
    tipo = "js"
    if "```" in texto_eli:
        partes = texto_eli.split("```")
        if len(partes) > 1:
            codigo_bruto = partes[1].strip()
            linhas = codigo_bruto.split('\n')
            if linhas and linhas[0].lower() in ['js', 'javascript', 'html', 'css']:
                codigo = '\n'.join(linhas[1:])
            else:
                codigo = codigo_bruto

    # Tratamento do Firestore sem bloquear a resposta do chat
    try:
        firebase_key = os.environ.get("FIREBASE_KEY")
        if firebase_key and not firebase_admin._apps:
            cred_dict = json.loads(firebase_key)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        
        if firebase_admin._apps:
            db = firestore.client()
            db.collection("chats").add({"pergunta": pergunta, "resposta": texto_eli})
    except Exception as e:
        print(f"Erro Firebase: {e}")
    
    return jsonify({"resposta": texto_eli, "codigo": codigo, "tipo": tipo})
