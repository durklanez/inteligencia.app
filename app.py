import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # pip install flask-cors
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq # pip install groq

app = Flask(__name__)
CORS(app) # Libera o frontend falar com o backend

# GROQ
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# FIREBASE
firebase_key_str = os.getenv("FIREBASE_KEY")
if firebase_key_str:
    cred_dict = json.loads(firebase_key_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

# SERVE O HTML
@app.route("/")
def serve_frontend():
    return send_from_directory('.', 'index.html')

# API DO ELI
@app.route("/teste-firestore", methods=["POST"])
def chat_eli():
    data = request.get_json()
    pergunta = data.get('pergunta')
    historico = data.get('historico', [])

    # PROMPT DO SISTEMA PRA ELI SABER QUE É PROGRAMADOR
    system_prompt = """
    Você é o Eli AI, um assistente programador br. Responde em pt-br, gíria "wy".
    Se o usuário pedir código, você DEVE responder em JSON com 2 campos:
    "resposta": texto explicando o código
    "codigo": o código completo

    Se NÃO for pedido código, responde só com "resposta": texto normal.
    Exemplo se pedirem soma:
    {"resposta": "Pronto wy! Fiz uma função de soma pra ti", "codigo": "function soma(a,b){return a+b}"}
    """

    mensagens = [{"role": "system", "content": system_prompt}]
    mensagens.extend(historico)
    mensagens.append({"role": "user", "content": pergunta})

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant", # modelo rápido e grátis
            messages=mensagens,
            temperature=0.7,
            response_format={"type": "json_object"} # Força retornar JSON
        )

        resposta_json = json.loads(completion.choices[0].message.content)

        # Salva no Firebase se quiser
        # db.collection("chats").add({"pergunta": pergunta, "resposta": resposta_json})

        return jsonify(resposta_json)

    except Exception as e:
        return jsonify({"resposta": f"Erro no Eli: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
