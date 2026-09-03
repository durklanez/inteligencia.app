from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
from google import genai
from google.genai import types

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ============================================================
# GEMINI
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

# UM ÚNICO MODELO
gemini_model = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

client = None

if api_key:
    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=20000
            )
        )

        print("Gemini inicializado com sucesso.")
        print("Modelo:", gemini_model)

    except Exception as e:
        print("ERRO AO INICIALIZAR GEMINI:", repr(e))

else:
    print("ERRO: GEMINI_API_KEY não encontrada.")


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# ============================================================
# TESTE
# ============================================================

@app.route("/teste")
def teste():

    return jsonify({
        "status": "online",
        "gemini": client is not None,
        "modelo": gemini_model,
        "firebase": False
    })


# ============================================================
# VERIFICAR ERRO TEMPORÁRIO
# ============================================================

def erro_temporario(erro):

    texto = str(erro).upper()

    return (
        "503" in texto
        or "UNAVAILABLE" in texto
        or "429" in texto
        or "RESOURCE_EXHAUSTED" in texto
        or "DEADLINE_EXCEEDED" in texto
        or "TIMEOUT" in texto
    )


# ============================================================
# CHAMAR GEMINI
# ============================================================

def chamar_gemini(contents):

    ultimo_erro = None

    # No máximo 2 tentativas.
    # É o MESMO modelo, não são 3 modelos.
    for tentativa in range(2):

        try:

            print(
                f"Tentativa Gemini: "
                f"{tentativa + 1}/2"
            )

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
                        "use blocos de código com a linguagem correta."
                    ),

                    temperature=0.7,

                    max_output_tokens=1024
                )
            )

            resposta = response.text

            if resposta:

                print(
                    "GEMINI RESPONDEU COM SUCESSO."
                )

                return resposta

            print(
                "Gemini respondeu sem texto."
            )

            return "Não consegui gerar uma resposta agora."

        except Exception as e:

            ultimo_erro = e

            print("========================================")
            print("ERRO GEMINI")
            print("TENTATIVA:", tentativa + 1)
            print("ERRO:", repr(e))
            print("========================================")

            # Se não for erro temporário,
            # não tenta novamente.
            if not erro_temporario(e):
                raise e

            # Se foi a primeira tentativa,
            # espera apenas 0.7 segundo.
            if tentativa == 0:

                print(
                    "Erro temporário. "
                    "Tentando novamente..."
                )

                time.sleep(0.7)

    raise ultimo_erro


# ============================================================
# TESTE FIRESTORE / GEMINI
# ============================================================

@app.route("/teste-firestore", methods=["POST", "OPTIONS"])
def teste_firestore():

    if request.method == "OPTIONS":
        return "", 200

    try:

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
        # PERGUNTA VAZIA
        # ----------------------------------------------------

        if not pergunta:

            return jsonify({
                "resposta": "Digite uma mensagem para a Eli.",
                "codigo": "",
                "tipo": "js"
            })

        # ----------------------------------------------------
        # GEMINI NÃO CONFIGURADO
        # ----------------------------------------------------

        if client is None:

            return jsonify({
                "resposta": (
                    "❌ GEMINI_API_KEY não está "
                    "configurada no Render."
                ),
                "codigo": "",
                "tipo": "js"
            }), 500

        # ----------------------------------------------------
        # HISTÓRICO
        # ----------------------------------------------------

        contents = []

        # Somente últimas 6 mensagens
        if isinstance(historico, list):

            for msg in historico[-6:]:

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
        # PERGUNTA ATUAL
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
        print("MODELO:", gemini_model)
        print("========================================")

        # ----------------------------------------------------
        # GEMINI
        # ----------------------------------------------------

        resposta = chamar_gemini(
            contents
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
                    linguagem = (
                        linhas[0]
                        .strip()
                        .lower()
                    )

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
        # RESPOSTA FINAL
        # ----------------------------------------------------

        return jsonify({

            "resposta": resposta,

            "codigo": codigo,

            "tipo": tipo,

            "modelo": gemini_model,

            "status": "ok"

        })

    # ========================================================
    # ERRO
    # ========================================================

    except Exception as e:

        erro = repr(e)

        print("========================================")
        print("ERRO REAL DO GEMINI/SERVIDOR")
        print("========================================")
        print(erro)
        print("========================================")

        if erro_temporario(e):

            return jsonify({

                "resposta": (
                    "⚠️ O Gemini está temporariamente "
                    "indisponível. Tenta novamente."
                ),

                "codigo": "",

                "tipo": "js",

                "modelo": gemini_model,

                "status": "temporarily_unavailable"

            }), 503

        return jsonify({

            "resposta": "❌ Erro no servidor.",

            "codigo": "",

            "tipo": "js",

            "modelo": gemini_model,

            "status": "error",

            "erro": erro

        }), 500


# ============================================================
# START
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
