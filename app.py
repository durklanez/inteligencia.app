from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
from google.genai import types

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Inicializa o cliente do Gemini
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# Inicialização do Firebase
firebase_key = os.environ.get("FIREBASE_KEY")
if firebase_key and not firebase_admin._apps:
    try:
        cred_dict = json.loads(firebase_key)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Erro ao inicializar Firebase: {e}")

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/teste-firestore', methods=['POST', 'OPTIONS'])
def teste_firestore():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json() or {}
    pergunta = data.get('pergunta', '')
    historico_bruto = data.get('historico', [])

    if not api_key or not client:
        return jsonify({
            "resposta": "Erro: A variável GEMINI_API_KEY não foi configurada no Render.",
            "codigo": "",
            "tipo": "js"
        })

    try:
        # Formatação do histórico
        contents = []
        for msg in historico_bruto:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })
        
        contents.append({
            "role": "user",
            "parts": [{"text": pergunta}]
        })

        # Chamada com o modelo atualizado (gemini-2.5-flash)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="Você é a Eli AI. Responde em pt-br curta."
            )
        )
        texto_eli = response.text

    except Exception as e:
        texto_eli = f"Erro Gemini: {str(e)}"

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

    if firebase_admin._apps:
        try:
            db = firestore.client()
            db.collection("chats").add({"pergunta": pergunta, "resposta": texto_eli})
        except Exception as e:
            print(f"Erro ao salvar no Firestore: {e}")
    
    return jsonify({"resposta": texto_eli, "codigo": codigo, "tipo": tipo})
