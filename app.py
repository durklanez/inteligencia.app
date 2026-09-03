from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time

from google import genai
from google.genai import types


# ==========================================
# FLASK
# ==========================================

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)


# ==========================================
# CONFIGURAÇÃO
# ==========================================

api_key = os.environ.get("GEMINI_API_KEY")

gemini_model = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.7-flash"
)

client = None


# ==========================================
# INICIALIZAR GEMINI
# ==========================================

if api_key:

    try:

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30000
            )
        )

        print("========================================")
        print("GEMINI INICIALIZADO COM SUCESSO")
        print("MODELO:", gemini_model)
        print("TIMEOUT: 30 segundos")
        print("========================================")

    except Exception as e:

        print("========================================")
        print("ERRO AO INICIALIZAR GEMINI")
        print("TIPO:", type(e).__name__)
        print("ERRO:", repr(e))
        print("========================================")

else:

    print("========================================")
    print("ERRO: GEMINI_API_KEY NÃO ENCONTRADA")
    print("========================================")


# ==========================================
# DETECTAR ERROS TEMPORÁRIOS
# ==========================================

def erro_temporario(erro):

    texto = str(erro).upper()

    nome = type(erro).__name__.upper()

    return (
        "503" in texto
        or "UNAVAILABLE" in texto
        or "429" in texto
        or "RESOURCE_EXHAUSTED" in texto
        or "DEADLINE_EXCEEDED" in texto
        or "TIMEOUT" in texto
        or "READTIMEOUT" in nome
        or "CONNECTTIMEOUT" in nome
        or "REMOTEPROTOCOLERROR" in nome
        or "SERVICEUNAVAILABLE" in nome
    )


# ==========================================
# CHAMAR GEMINI
# ==========================================

def chamar_gemini(contents):

    ultimo_erro = None

    for tentativa in range(1, 3):

        inicio = time.time()

        try:

            print("----------------------------------------")
            print(f"Tentativa Gemini: {tentativa}/2")
            print("Modelo:", gemini_model)
            print("----------------------------------------")

            response = client.models.generate_content(

                model=gemini_model,

                contents=contents,

                config=types.GenerateContentConfig(

                    system_instruction=(
                        "Você é a Eli AI. "
                        "Responda sempre em português. "
                        "Seja rápida, clara e útil. "
                        "Ajude principalmente com programação. "
                        "Quando o usuário pedir código, "
                        "coloque o código dentro de um bloco "
                        "Markdown usando a linguagem correta. "
                        "Se o usuário pedir HTML, entregue HTML válido. "
                        "Não coloque código HTML usando # como título."
                    ),

                    temperature=0.7,

                    max_output_tokens=512
                )
            )

            tempo = round(
                time.time() - inicio,
                2
            )

            print("----------------------------------------")
            print("GEMINI RESPONDEU COM SUCESSO")
            print("TEMPO:", tempo, "segundos")
            print("----------------------------------------")

            return response

        except Exception as e:

            tempo = round(
                time.time() - inicio,
                2
            )

            ultimo_erro = e

            print("----------------------------------------")
            print("ERRO GEMINI")
            print("TENTATIVA:", tentativa)
            print("TEMPO:", tempo, "segundos")
            print("TIPO:", type(e).__name__)
            print("ERRO:", repr(e))
            print("----------------------------------------")

            if tentativa < 2 and erro_temporario(e):

                print(
                    "ERRO TEMPORÁRIO DETECTADO."
                )

                print(
                    "TENTANDO NOVAMENTE EM 0.5 SEGUNDOS..."
                )

                time.sleep(0.5)

                continue

            break

    raise ultimo_erro


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
def home():

    return send_from_directory(
        ".",
        "index.html"
    )


# ==========================================
# TESTE DO SERVIDOR
# ==========================================

@app.route("/teste")
def teste():

    return jsonify({

        "status": "online",

        "gemini": client is not None,

        "modelo": gemini_model,

        "firebase": False

    })


# ==========================================
# API ELI
# ==========================================

@app.route(
    "/teste-firestore",
    methods=["POST", "OPTIONS"]
)
def teste_firestore():

    # --------------------------------------
    # OPTIONS / CORS
    # --------------------------------------

    if request.method == "OPTIONS":

        return "", 200


    try:

        # ----------------------------------
        # RECEBER JSON
        # ----------------------------------

        data = request.get_json(
            silent=True
        )

        if not isinstance(data, dict):

            data = {}


        pergunta = str(
            data.get(
                "pergunta",
                ""
            )
        ).strip()


        historico = data.get(
            "historico",
            []
        )


        # ----------------------------------
        # PERGUNTA VAZIA
        # ----------------------------------

        if not pergunta:

            return jsonify({

                "resposta":
                    "Digite uma mensagem para a Eli.",

                "codigo": "",

                "tipo": "js"

            })


        # ----------------------------------
        # GEMINI NÃO CONFIGURADO
        # ----------------------------------

        if client is None:

            return jsonify({

                "resposta":
                    "❌ GEMINI_API_KEY não está configurada no Render.",

                "codigo": "",

                "tipo": "js"

            }), 500


        # ----------------------------------
        # PREPARAR HISTÓRICO
        # ----------------------------------

        contents = []


        if isinstance(
            historico,
            list
        ):

            for msg in historico[-6:]:

                if not isinstance(
                    msg,
                    dict
                ):
                    continue


                texto = msg.get(
                    "content"
                )


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


        # ----------------------------------
        # ADICIONAR PERGUNTA ATUAL
        # ----------------------------------

        if (

            not contents

            or contents[-1]["role"] != "user"

            or contents[-1]["parts"][0]["text"]
            != pergunta

        ):

            contents.append({

                "role": "user",

                "parts": [
                    {
                        "text": pergunta
                    }
                ]

            })


        # ----------------------------------
        # LOG
        # ----------------------------------

        print("")
        print("========================================")
        print("NOVA PERGUNTA")
        print("PERGUNTA:", pergunta)
        print("MODELO:", gemini_model)
        print("HISTÓRICO:", len(contents))
        print("========================================")


        # ----------------------------------
        # GEMINI
        # ----------------------------------

        response = chamar_gemini(
            contents
        )


        # ----------------------------------
        # RESPOSTA
        # ----------------------------------

        resposta = getattr(
            response,
            "text",
            None
        )


        if not resposta:

            resposta = (
                "Não consegui gerar uma resposta agora."
            )


        # ----------------------------------
        # EXTRAIR CÓDIGO
        # ----------------------------------

        codigo = ""

        tipo = "js"


        if "```" in resposta:

            partes = resposta.split("```")


            if len(partes) >= 2:

                bloco = partes[1].strip()


                linhas = bloco.split(
                    "\n"
                )


                linguagem = ""


                if linhas:

                    linguagem = (
                        linhas[0]
                        .strip()
                        .lower()
                    )


                mapa = {

                    "javascript": "js",

                    "js": "js",

                    "html": "html",

                    "htm": "html",

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

                    tipo = mapa[
                        linguagem
                    ]

                    codigo = "\n".join(
                        linhas[1:]
                    )

                else:

                    codigo = bloco


        # ----------------------------------
        # RESPOSTA FINAL
        # ----------------------------------

        print("TIPO DE CÓDIGO:", tipo)

        if codigo:

            print(
                "CÓDIGO ENCONTRADO: SIM"
            )

        else:

            print(
                "CÓDIGO ENCONTRADO: NÃO"
            )


        return jsonify({

            "resposta": resposta,

            "codigo": codigo,

            "tipo": tipo,

            "modelo": gemini_model

        })


    # ======================================
    # ERRO
    # ======================================

    except Exception as e:

        erro = repr(e)

        nome_erro = type(e).__name__


        print("")
        print("========================================")
        print("ERRO REAL DO GEMINI/SERVIDOR")
        print("TIPO:", nome_erro)
        print("ERRO:", erro)
        print("========================================")


        # ----------------------------------
        # ERRO TEMPORÁRIO
        # ----------------------------------

        if erro_temporario(e):

            return jsonify({

                "resposta":
                    "⏳ O Gemini demorou para responder. Tenta novamente.",

                "codigo": "",

                "tipo": "js",

                "modelo": gemini_model

            }), 503


        # ----------------------------------
        # ERRO NORMAL
        # ----------------------------------

        return jsonify({

            "resposta":
                "❌ Erro no servidor.",

            "codigo": "",

            "tipo": "js",

            "erro": erro,

            "modelo": gemini_model

        }), 500


# ==========================================
# INICIAR
# ==========================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "5000"
        )
    )

    print("========================================")
    print("SERVIDOR ELI AI INICIANDO")
    print("PORTA:", port)
    print("========================================")

    app.run(
        host="0.0.0.0",
        port=port
    )
