from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time

from groq import Groq


# ==========================================
# FLASK
# ==========================================

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)


# ==========================================
# CONFIGURAÇÃO GROQ
# ==========================================

api_key = os.environ.get("GROQ_API_KEY")

groq_model = os.environ.get(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

client = None


# ==========================================
# INICIALIZAR GROQ
# ==========================================

if api_key:

    try:

        client = Groq(
            api_key=api_key,
            timeout=30.0
        )

        print("========================================")
        print("GROQ INICIALIZADO COM SUCESSO")
        print("MODELO:", groq_model)
        print("TIMEOUT: 30 segundos")
        print("========================================")

    except Exception as e:

        print("========================================")
        print("ERRO AO INICIALIZAR GROQ")
        print("TIPO:", type(e).__name__)
        print("ERRO:", repr(e))
        print("========================================")

else:

    print("========================================")
    print("ERRO: GROQ_API_KEY NÃO ENCONTRADA")
    print("========================================")


# ==========================================
# DETECTAR ERROS TEMPORÁRIOS
# ==========================================

def erro_temporario(erro):

    texto = str(erro).upper()
    nome = type(erro).__name__.upper()

    return (
        "503" in texto
        or "SERVICE_UNAVAILABLE" in texto
        or "TIMEOUT" in texto
        or "READTIMEOUT" in nome
        or "CONNECTTIMEOUT" in nome
        or "REMOTEPROTOCOLERROR" in nome
    )


# ==========================================
# DETECTAR RATE LIMIT
# ==========================================

def erro_rate_limit(erro):

    texto = str(erro).upper()
    nome = type(erro).__name__.upper()

    return (
        "429" in texto
        or "RATE_LIMIT" in texto
        or "RATELIMIT" in texto
        or "TOO MANY REQUESTS" in texto
        or "RESOURCE_EXHAUSTED" in texto
        or "RATE" in nome
    )


# ==========================================
# CHAMAR GROQ
# ==========================================

def chamar_groq(messages):

    ultimo_erro = None

    for tentativa in range(1, 3):

        inicio = time.time()

        try:

            print("----------------------------------------")
            print(f"Tentativa Groq: {tentativa}/2")
            print("Modelo:", groq_model)
            print("----------------------------------------")

            response = client.chat.completions.create(

                model=groq_model,

                messages=messages,

                temperature=0.7,

                max_tokens=512
            )

            tempo = round(
                time.time() - inicio,
                2
            )

            print("----------------------------------------")
            print("GROQ RESPONDEU COM SUCESSO")
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
            print("ERRO GROQ")
            print("TENTATIVA:", tentativa)
            print("TEMPO:", tempo, "segundos")
            print("TIPO:", type(e).__name__)
            print("ERRO:", repr(e))
            print("----------------------------------------")

            # Não repetir 429
            if erro_rate_limit(e):

                print("RATE LIMIT / 429 DETECTADO.")
                print("NÃO VAI REPETIR A REQUISIÇÃO.")

                break

            # Repetir somente erros temporários
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
# TELA INICIAL
# ==========================================

@app.route("/")
def home():

    return send_from_directory(
        ".",
        "register.htm"
    )


# ==========================================
# TELA DE TRABALHO
# ==========================================

@app.route("/trabalhar")
def trabalhar():

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

        "groq": client is not None,

        "modelo": groq_model,

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
        # GROQ NÃO CONFIGURADO
        # ----------------------------------

        if client is None:

            return jsonify({

                "resposta":
                    "❌ GROQ_API_KEY não está configurada no Render.",

                "codigo": "",

                "tipo": "js",

                "modelo": groq_model

            }), 500


        # ----------------------------------
        # PREPARAR HISTÓRICO
        # ----------------------------------

        messages = [

            {
                "role": "system",

                "content": (
                    "Você é a Eli AI. "
                    "Responda sempre em português. "
                    "Seja rápida, clara e útil. "
                    "Ajude principalmente com programação. "
                    "Quando o usuário pedir código, "
                    "coloque o código dentro de um bloco "
                    "Markdown usando a linguagem correta. "
                    "Se o usuário pedir HTML, entregue HTML válido. "
                    "Não coloque código HTML usando # como título."
                )
            }

        ]


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

                    role = "assistant"

                else:

                    role = "user"


                messages.append({

                    "role": role,

                    "content": texto

                })


        # ----------------------------------
        # ADICIONAR PERGUNTA ATUAL
        # ----------------------------------

        if (

            len(messages) == 1

            or messages[-1]["role"] != "user"

            or messages[-1]["content"]
            != pergunta

        ):

            messages.append({

                "role": "user",

                "content": pergunta

            })


        # ----------------------------------
        # LOG
        # ----------------------------------

        print("")
        print("========================================")
        print("NOVA PERGUNTA")
        print("PERGUNTA:", pergunta)
        print("MODELO:", groq_model)
        print("HISTÓRICO:", len(messages))
        print("========================================")


        # ----------------------------------
        # GROQ
        # ----------------------------------

        response = chamar_groq(
            messages
        )


        # ----------------------------------
        # PEGAR RESPOSTA
        # ----------------------------------

        resposta = None

        try:

            resposta = (
                response
                .choices[0]
                .message
                .content
            )

        except Exception:

            resposta = None


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
        # LOG FINAL
        # ----------------------------------

        print(
            "TIPO DE CÓDIGO:",
            tipo
        )


        if codigo:

            print(
                "CÓDIGO ENCONTRADO: SIM"
            )

        else:

            print(
                "CÓDIGO ENCONTRADO: NÃO"
            )


        # ----------------------------------
        # RESPOSTA FINAL
        # ----------------------------------

        return jsonify({

            "resposta": resposta,

            "codigo": codigo,

            "tipo": tipo,

            "modelo": groq_model

        })


    # ======================================
    # ERRO
    # ======================================

    except Exception as e:

        erro = repr(e)

        nome_erro = type(e).__name__


        print("")
        print("========================================")
        print("ERRO REAL DO GROQ/SERVIDOR")
        print("TIPO:", nome_erro)
        print("ERRO:", erro)
        print("========================================")


        # ----------------------------------
        # RATE LIMIT / 429
        # ----------------------------------

        if erro_rate_limit(e):

            return jsonify({

                "resposta":
                    "⚠️ O limite da API Groq foi atingido. "
                    "Aguarda o limite renovar e tenta novamente.",

                "codigo": "",

                "tipo": "js",

                "modelo": groq_model

            }), 429


        # ----------------------------------
        # ERRO TEMPORÁRIO
        # ----------------------------------

        if erro_temporario(e):

            return jsonify({

                "resposta":
                    "⏳ A Groq demorou para responder. "
                    "Tenta novamente.",

                "codigo": "",

                "tipo": "js",

                "modelo": groq_model

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

            "modelo": groq_model

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
