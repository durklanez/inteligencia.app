from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
from google.genai import types
import threading

app = Flask(name, static_folder='.', static_url_path='')
CORS(app)

=========================================================

GEMINI

=========================================================

api_key = os.environ.get("GEMINI_API_KEY")

gemini_model = os.environ.get(
"GEMINI_MODEL",
"gemini-3.6-flash"
)

client = genai.Client(api_key=api_key) if api_key else None

=========================================================

FIREBASE

=========================================================

firebase_key = os.environ.get("FIREBASE_KEY")

if firebase_key and not firebase_admin._apps:

try:

    cred_dict = json.loads(firebase_key)

    cred = credentials.Certificate(
        cred_dict
    )

    firebase_admin.initialize_app(
        cred
    )

    print(
        "Firebase inicializado com sucesso."
    )

except Exception as e:

    print(
        f"Erro ao inicializar Firebase: {e}"
    )

=========================================================

PÁGINA PRINCIPAL

=========================================================

@app.route('/')
def home():

return send_from_directory(
    '.',
    'index.html'
)

=========================================================

TESTE

=========================================================

@app.route('/teste', methods=['GET'])
def teste():

return jsonify({

    "status": "online",

    "gemini": bool(client),

    "modelo": gemini_model,

    "firebase": bool(
        firebase_admin._apps
    )

})

=========================================================

SALVAR FIREBASE SEM BLOQUEAR A RESPOSTA

=========================================================

def salvar_chat(pergunta, resposta):

if not firebase_admin._apps:
    return

try:

    db = firestore.client()

    db.collection("chats").add({

        "pergunta": pergunta,

        "resposta": resposta

    })

    print(
        "Chat salvo no Firestore."
    )

except Exception as e:

    print(
        f"Erro ao salvar no Firestore: {e}"
    )

=========================================================

CHAT ELI AI

=========================================================

@app.route(
'/teste-firestore',
methods=['POST', 'OPTIONS']
)
def teste_firestore():

if request.method == 'OPTIONS':

    return '', 200


data = request.get_json(
    silent=True
) or {}


pergunta = str(
    data.get(
        'pergunta',
        ''
    )
).strip()


historico_bruto = data.get(
    'historico',
    []
)


# =====================================================
# VERIFICAR API
# =====================================================

if not api_key or not client:

    return jsonify({

        "resposta":
            "Erro: A variável GEMINI_API_KEY "
            "não foi configurada no Render.",

        "codigo": "",

        "tipo": "js"

    }), 500


if not pergunta:

    return jsonify({

        "resposta":
            "Escreve alguma coisa para a Eli.",

        "codigo": "",

        "tipo": "js"

    })


# =====================================================
# HISTÓRICO
# =====================================================

try:

    contents = []


    # Somente mensagens anteriores.
    # A pergunta atual já será adicionada abaixo.

    historico_recente = (
        historico_bruto[-10:]
        if isinstance(
            historico_bruto,
            list
        )
        else []
    )


    for msg in historico_recente:

        if not isinstance(
            msg,
            dict
        ):
            continue


        role = (
            "user"
            if msg.get("role") == "user"
            else "model"
        )


        texto = msg.get(
            "content",
            ""
        )


        if not texto:
            continue


        contents.append({

            "role": role,

            "parts": [

                {
                    "text": str(texto)
                }

            ]

        })


    # =================================================
    # PERGUNTA ATUAL
    # =================================================

    contents.append({

        "role": "user",

        "parts": [

            {
                "text": pergunta
            }

        ]

    })


    # =================================================
    # GEMINI
    # =================================================

    print(
        f"Chamando Gemini: {gemini_model}"
    )


    response = client.models.generate_content(

        model=gemini_model,

        contents=contents,

        config=types.GenerateContentConfig(

            system_instruction=(
                "Você é a Eli AI. "
                "Responda sempre em português do Brasil. "
                "Seja clara, útil e direta. "
                "Não seja desnecessariamente longa. "
                "Quando o usuário pedir código, "
                "forneça o código dentro de blocos "
                "de código usando a linguagem correta."
            ),

            temperature=0.7

        )

    )


    texto_eli = (
        response.text
        or "Não consegui gerar uma resposta."
    )


    print(
        "Gemini respondeu."
    )


except Exception as e:

    print(
        f"Erro Gemini: {str(e)}"
    )


    return jsonify({

        "resposta":
            "❌ A Eli encontrou um erro temporário. "
            "Tenta novamente.",

        "codigo": "",

        "tipo": "js"

    }), 500


# =====================================================
# EXTRAIR CÓDIGO
# =====================================================

codigo = ""

tipo = "js"


if "```" in texto_eli:

    partes = texto_eli.split("```")


    if len(partes) > 1:

        codigo_bruto = (
            partes[1].strip()
        )


        linhas = codigo_bruto.split(
            '\n'
        )


        if linhas:

            linguagem = (
                linhas[0]
                .strip()
                .lower()
            )


            linguagens = {

                "js": "js",

                "javascript": "js",

                "html": "html",

                "css": "css",

                "python": "python",

                "py": "python",

                "json": "json",

                "java": "java",

                "c": "c",

                "cpp": "cpp",

                "c++": "cpp",

                "php": "php",

                "sql": "sql",

                "typescript": "typescript",

                "ts": "typescript"

            }


            if linguagem in linguagens:

                tipo = linguagens[
                    linguagem
                ]

                codigo = '\n'.join(
                    linhas[1:]
                )

            else:

                codigo = codigo_bruto


# =====================================================
# FIREBASE EM SEGUNDO PLANO
# =====================================================

threading.Thread(

    target=salvar_chat,

    args=(
        pergunta,
        texto_eli
    ),

    daemon=True

).start()


# =====================================================
# RESPOSTA
# =====================================================

return jsonify({

    "resposta": texto_eli,

    "codigo": codigo,

    "tipo": tipo,

    "modelo": gemini_model

})

=========================================================

EXECUTAR

=========================================================

if name == 'main':

port = int(
    os.environ.get(
        "PORT",
        5000
    )
)


app.run(

    host='0.0.0.0',

    port=port

)
