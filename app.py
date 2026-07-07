from flask import Flask, request, jsonify, send_from_directory
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq

app = Flask(__name__, static_folder='.', static_url_path='')

# GROQ
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# FIREBASE
firebase_key = os.environ.get("FIREBASE_KEY")
cred_dict = json.loads(firebase_key)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/teste-firestore', methods=['POST'])
def teste_firestore():
    data = request.get_json()
    pergunta = data.get('pergunta', '')
    historico = data.get('historico', [])

    mensagens = [{"role": "system", "content": "Você é a Eli AI. Responde em pt-br, curta. Se for código usa ```linguagem\ncodigo\n```"}] + historico + [{"role": "user", "content": pergunta}]

    chat_completion = client.chat.completions.create(messages=mensagens, model="llama-3.1-8b-instant")
    texto_eli = chat_completion.choices[0].message.content

    codigo = ""
    tipo = "js"
    if "```" in texto_eli:
        partes = texto_eli.split("```")
        codigo = partes[1].strip()
        if codigo.startswith("python"): tipo="py"; codigo=codigo.replace("python\n","")
        elif codigo.startswith("html"): tipo="html"; codigo=codigo.replace("html\n","")
        elif codigo.startswith("css"): tipo="css"; codigo=codigo.replace("css\n","")
        elif codigo.startswith("js"): tipo="js"; codigo=codigo.replace("js\n","")

    db.collection("chats").add({"pergunta": pergunta, "resposta": texto_eli, "timestamp": firestore.SERVER_TIMESTAMP})
    return jsonify({"resposta": texto_eli, "codigo": codigo, "tipo": tipo})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
