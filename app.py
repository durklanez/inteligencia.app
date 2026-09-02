from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import time
import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
from google.genai import types

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# =========================================================
# GEMINI
# =========================================================

api_key = os.environ.get("GEMINI_API_KEY")

# Pode mudar a versão pelo Render
# Se GEMINI_MODEL não existir, usa gemini-3.6-flash
gemini_model = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

client = genai.Client(api_key=api_key) if api_key else None


# =========================================================
# FIREBASE
# =========================================================

firebase_key = os.environ.get("FIREBASE_KEY")

if firebase_key and not firebase_admin._apps:
    try:
        cred_dict = json.loads(firebase_key)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

        print("Firebase inicializado com sucesso.")

    except Exception as e:
        print(f"Erro ao inicializar Firebase: {e}")


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


# =========================================================
# TESTE DO SERVIDOR
# =========================================================

@app.route('/teste', methods=['GET'])
def teste():

    return jsonify({
        "status": "online",
        "gemini": bool(client),
        "modelo": gemini_model,
        "firebase": bool(firebase_admin._apps)
    })


# =========================================================
# CHAT ELI AI
# =========================================================

@app.route('/teste-firestore', methods=['POST', 'OPTIONS'])
def teste_firestore():

    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json() or {}

    pergunta = data.get('pergunta', '')

    historico_bruto = data.get(
        'historico',
        []
    )


    # =====================================================
    # VERIFICAR API KEY
    # =====================================================

    if not api_key or not client:

        return jsonify({
            "resposta": (
                "Erro: A variável GEMINI_API_KEY "
                "não foi configurada no Render."
            ),
            "codigo": "",
            "tipo": "js"
        })


    # =====================================================
    # PREPARAR HISTÓRICO
    # =====================================================

    try:

        contents = []

        for msg in historico_bruto:

            if not isinstance(msg, dict):
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
                    "text": str(pergunta)
                }
            ]
        })


        # =================================================
        # GEMINI COM RETRY + FALLBACK AUTOMÁTICO
        # =================================================

        # Mantém o modelo configurado no Render como principal.
        # Depois usa modelos alternativos caso haja 503,
        # indisponibilidade temporária ou outro erro de modelo.

        modelos = [
            gemini_model,
            "gemini-3.7-flash",
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite"
        ]

        # Remove modelos duplicados mantendo a ordem.
        modelos = list(dict.fromkeys(modelos))

        response = None
        ultimo_erro = None
        modelo_usado = None


        for modelo in modelos:

            # Cada modelo pode ser tentado até 2 vezes.
            for tentativa in range(2):

                try:

                    print(
                        f"Tentando modelo: {modelo} "
                        f"(tentativa {tentativa + 1}/2)"
                    )

                    response = client.models.generate_content(

                        model=modelo,

                        contents=contents,

                        config=types.GenerateContentConfig(

                            system_instruction=(
                                "Você é a Eli AI. "
                                "Responda sempre em português do Brasil. "
                                "Seja clara, útil e direta. "
                                "Quando o usuário pedir código, "
                                "forneça o código dentro de blocos "
                                "de código usando a linguagem correta."
                            )
                        )
                    )

                    modelo_usado = modelo

                    print(
                        f"Modelo funcionando: {modelo}"
                    )

                    break


                except Exception as e:

                    ultimo_erro = e

                    erro_texto = str(e)

                    print(
                        f"Modelo {modelo} falhou: "
                        f"{erro_texto}"
                    )


                    # Se for uma falha temporária,
                    # espera antes de tentar novamente.
                    if (
                        "503" in erro_texto
                        or "UNAVAILABLE" in erro_texto.upper()
                        or "high demand" in erro_texto.lower()
                        or "temporarily" in erro_texto.lower()
                    ):

                        if tentativa == 0:

                            print(
                                "Serviço temporariamente "
                                "indisponível. "
                                "Aguardando 3 segundos..."
                            )

                            time.sleep(3)

                    else:

                        # Para outros erros, não desperdiça
                        # a segunda tentativa do mesmo modelo.
                        break


            # Se conseguiu resposta, para o fallback.
            if response is not None:
                break


        # =================================================
        # SE TODOS OS MODELOS FALHAREM
        # =================================================

        if response is None:

            print(
                "Todos os modelos Gemini falharam."
            )

            # Não mostra o erro técnico completo para o usuário.
            texto_eli = (
                "Desculpa, a Eli AI está temporariamente "
                "com muita demanda. Tenta novamente em "
                "alguns segundos."
            )

            modelo_usado = gemini_model

        else:

            texto_eli = response.text or (
                "Não consegui gerar uma resposta."
            )


    except Exception as e:

        print(
            f"Erro Gemini: {str(e)}"
        )

        texto_eli = (
            "Desculpa, ocorreu um erro temporário "
            "ao gerar a resposta. Tenta novamente."
        )

        modelo_usado = gemini_model


    # =====================================================
    # EXTRAIR CÓDIGO
    # =====================================================

    codigo = ""
    tipo = "js"


    if "```" in texto_eli:

        partes = texto_eli.split("```")


        if len(partes) > 1:

            codigo_bruto = partes[1].strip()

            linhas = codigo_bruto.split('\n')


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

                    tipo = linguagens[linguagem]

                    codigo = '\n'.join(
                        linhas[1:]
                    )

                else:

                    codigo = codigo_bruto


    # =====================================================
    # SALVAR NO FIREBASE
    # =====================================================

    if firebase_admin._apps:

        try:

            db = firestore.client()

            db.collection("chats").add({

                "pergunta": pergunta,

                "resposta": texto_eli

            })

            print(
                "Chat salvo no Firestore."
            )

        except Exception as e:

            print(
                f"Erro ao salvar no Firestore: {e}"
            )


    # =====================================================
    # ENVIAR PARA O INDEX.HTML
    # =====================================================

    return jsonify({

        "resposta": texto_eli,

        "codigo": codigo,

        "tipo": tipo,

        "modelo": modelo_usado

    })


# =========================================================
# EXECUTAR
# =========================================================

if __name__ == '__main__':

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
