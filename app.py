from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
from google import genai
from google.genai import types

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ============================================================
# CONFIGURAÇÃO DO GEMINI
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

# Modelo principal
gemini_model = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

# Modelos de fallback
fallback_models = [
    gemini_model,
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite"
]

# Remove modelos repetidos
modelos = []
for modelo in fallback_models:
    if modelo and modelo not in modelos:
        modelos.append(modelo)

client = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Gemini inicializado com sucesso.")
        print("Modelos disponíveis para fallback:", modelos)

    except Exception as e:
        print("ERRO AO INICIALIZAR GEMINI:", repr(e))

else:
    print("ERRO: GEMINI_API_KEY não encontrada.")


# ============================================================
# FUNÇÃO PARA DETECTAR ERROS TEMPORÁRIOS
# ============================================================

def erro_temporario(erro):
    """
    Detecta erros como:
    503 UNAVAILABLE
    429 RESOURCE_EXHAUSTED
    500 INTERNAL
    502 BAD GATEWAY
    504 GATEWAY TIMEOUT
    """

    texto = str(erro).upper()

    codigos = [
        "503",
        "UNAVAILABLE",
        "429",
        "RESOURCE_EXHAUSTED",
        "500",
        "INTERNAL",
        "502",
        "BAD GATEWAY",
        "504",
        "GATEWAY TIMEOUT"
    ]

    return any(codigo in texto for codigo in codigos)


# ============================================================
# CHAMADA GEMINI COM FALLBACK
# ============================================================

def gerar_resposta(contents):

    if client is None:
        raise Exception("GEMINI_API_KEY não configurada.")

    ultimo_erro = None

    for indice, modelo in enumerate(modelos):

        print("----------------------------------------")
        print("Tentando modelo:", modelo)
        print("----------------------------------------")

        try:

            response = client.models.generate_content(
                model=modelo,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "Você é a Eli AI. "
                        "Responda sempre em português. "
                        "Seja rápida, clara e útil. "
                        "Ajude principalmente com programação. "
                        "Quando o usuário pedir código, "
                        "use blocos de código com a linguagem correta."
                    ),
                    temperature=0.7,
                    max_output_tokens=2048
                )
            )

            resposta = response.text

            if resposta:

                print("GEMINI RESPONDEU COM SUCESSO.")
                print("MODELO USADO:", modelo)

                return resposta, modelo

            print("Modelo respondeu sem texto.")

        except Exception as e:

            ultimo_erro = e

            print("----------------------------------------")
            print("ERRO NO MODELO:", modelo)
            print(repr(e))
            print("----------------------------------------")

            # Se for erro temporário, tenta o próximo modelo
            if erro_temporario(e):

                print(
                    "Erro temporário detectado. "
                    "Tentando próximo modelo..."
                )

                # Pequena espera somente antes do fallback
                if indice < len(modelos) - 1:
                    time.sleep(1)
                    continue

            else:
                # Erros que não são temporários
                # não adianta ficar tentando modelos diferentes
                raise e

    # Se todos os modelos falharam
    if ultimo_erro:
        raise ultimo_erro

    raise Exception("Nenhum modelo conseguiu gerar resposta.")


# ============================================================
# ROTA PRINCIPAL
# ============================================================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# ============================================================
# TESTE DO SERVIDOR
# ============================================================

@app.route("/teste")
def teste():

    return jsonify({
        "status": "online",
        "gemini": client is not None,
        "modelo_principal": gemini_model,
        "modelos_fallback": modelos,
        "firebase": False
    })


# ============================================================
# TESTE FIRESTORE / GEMINI
# ============================================================

@app.route("/teste-firestore", methods=["POST", "OPTIONS"])
def teste_firestore():

    if request.method == "OPTIONS":
        return "", 200

    try:

        # ----------------------------------------------------
        # RECEBER JSON
        # ----------------------------------------------------

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            data = {}

        pergunta = str(
            data.get("pergunta", "")
        ).strip()

        historico = data.get(
            "historico",
            []
        )

        # ----------------------------------------------------
        # VERIFICAR PERGUNTA
        # ----------------------------------------------------

        if not pergunta:

            return jsonify({
                "resposta": "Digite uma mensagem para a Eli.",
                "codigo": "",
                "tipo": "js"
            })

        # ----------------------------------------------------
        # VERIFICAR GEMINI
        # ----------------------------------------------------

        if client is None:

            return jsonify({
                "resposta": "❌ GEMINI_API_KEY não está configurada no Render.",
                "codigo": "",
                "tipo": "js"
            }), 500

        # ----------------------------------------------------
        # MONTAR HISTÓRICO
        # ----------------------------------------------------

        contents = []

        if isinstance(historico, list):

            for msg in historico[-10:]:

                if not isinstance(msg, dict):
                    continue

                texto = msg.get("content")

                if not texto:
                    continue

                texto = str(texto)

                role = msg.get(
                    "role",
                    "user"
                )

                if role == "assistant":
                    role = "model"
                else:
                    role = "user"

                contents.append({
                    "role": role,
                    "parts": [
                        {
                            "text": texto
                        }
                    ]
                })

        # ----------------------------------------------------
        # EVITAR DUPLICAÇÃO DA PERGUNTA
        # ----------------------------------------------------

        if (
            not contents
            or contents[-1]["role"] != "user"
            or contents[-1]["parts"][0]["text"] != pergunta
        ):

            contents.append({
                "role": "user",
                "parts": [
                    {
                        "text": pergunta
                    }
                ]
            })

        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        print("")
        print("========================================")
        print("NOVA PERGUNTA")
        print("========================================")
        print("PERGUNTA:", pergunta)
        print("MODELO PRINCIPAL:", gemini_model)
        print("========================================")

        # ----------------------------------------------------
        # CHAMAR GEMINI COM FALLBACK
        # ----------------------------------------------------

        resposta, modelo_usado = gerar_resposta(
            contents
        )

        # ----------------------------------------------------
        # GARANTIR RESPOSTA
        # ----------------------------------------------------

        if not resposta:

            resposta = (
                "Não consegui gerar uma resposta agora."
            )

        # ----------------------------------------------------
        # EXTRAIR CÓDIGO
        # ----------------------------------------------------

        codigo = ""
        tipo = "js"

        if "```" in resposta:

            partes = resposta.split("```")

            if len(partes) >= 2:

                bloco = partes[1].strip()

                linhas = bloco.split("\n")

                linguagem = ""

                if linhas:
                    linguagem = linhas[0].strip().lower()

                mapa = {

                    "javascript": "js",
                    "js": "js",

                    "html": "html",

                    "css": "css",

                    "python": "py",
                    "py": "py",

                    "typescript": "ts",
                    "ts": "ts",

                    "json": "json",

                    "java": "java",

                    "php": "php",

                    "sql": "sql",

                    "c": "c",

                    "cpp": "cpp",
                    "c++": "cpp"
                }

                if linguagem in mapa:

                    tipo = mapa[linguagem]

                    codigo = "\n".join(
                        linhas[1:]
                    )

                else:

                    codigo = bloco

        # ----------------------------------------------------
        # RESPOSTA
        # ----------------------------------------------------

        return jsonify({

            "resposta": resposta,

            "codigo": codigo,

            "tipo": tipo,

            "modelo": modelo_usado,

            "status": "ok"

        })

    # ========================================================
    # ERRO
    # ========================================================

    except Exception as e:

        erro = repr(e)

        print("")
        print("========================================")
        print("ERRO REAL DO GEMINI/SERVIDOR")
        print("========================================")
        print(erro)
        print("========================================")

        # ----------------------------------------------------
        # ERRO TEMPORÁRIO
        # ----------------------------------------------------

        if erro_temporario(e):

            return jsonify({

                "resposta": (
                    "⚠️ O Gemini está temporariamente ocupado. "
                    "Tente novamente em alguns segundos."
                ),

                "codigo": "",

                "tipo": "js",

                "erro": erro,

                "status": "temporarily_unavailable"

            }), 503

        # ----------------------------------------------------
        # OUTRO ERRO
        # ----------------------------------------------------

        return jsonify({

            "resposta": (
                "❌ Ocorreu um erro no servidor."
            ),

            "codigo": "",

            "tipo": "js",

            "erro": erro,

            "status": "error"

        }), 500


# ============================================================
# START DO FLASK
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "5000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
