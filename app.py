from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from google import genai
from google.genai import types

# =========================================================
# APP
# =========================================================

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# =========================================================
# GEMINI
# =========================================================

api_key = os.environ.get("GEMINI_API_KEY")

gemini_model = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

client = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Gemini inicializado com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar Gemini: {e}")

# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# =========================================================
# TESTE DO SERVIDOR
# =========================================================

@app.route("/teste", methods=["GET"])
def teste():
    return jsonify({
        "status": "online",
        "gemini": bool(client),
        "modelo": gemini_model,
        "firebase": False
    })


# =========================================================
# CHAT DA ELI
# =========================================================

@app.route("/teste-firestore", methods=["POST", "OPTIONS"])
def teste_firestore():

    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}

    pergunta = str(
        data.get("pergunta", "")
    ).strip()

    historico_bruto = data.get(
        "historico",
        []
    )

    if not pergunta:
        return jsonify({
            "resposta": "Digite alguma coisa para falar comigo wy 😄",
            "codigo": "",
            "tipo": "js"
        })

    if not api_key or not client:
        return jsonify({
            "resposta": (
                "❌ A GEMINI_API_KEY não está configurada "
                "corretamente no Render."
            ),
            "codigo": "",
            "tipo": "js"
        }), 500

    try:

        # =================================================
        # HISTÓRICO
        # =================================================

        contents = []

        if isinstance(historico_bruto, list):

            historico_recente = historico_bruto[-10:]

            for msg in historico_recente:

                if not isinstance(msg, dict):
                    continue

                texto = msg.get(
                    "content",
                    ""
                )

                if not texto:
                    continue

                texto = str(texto)

                role_original = msg.get(
                    "role",
                    "user"
                )

                if role_original == "assistant":
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
                    "Responda em português do Brasil. "
                    "Seja rápida, clara, útil e direta. "
                    "Pode ajudar com programação, HTML, CSS, "
                    "JavaScript, Python e outros assuntos. "
                    "Quando o usuário pedir código, "
                    "entregue o código em bloco de código "
                    "com a linguagem correta."
                )
            )
        )

        texto_eli = response.text

        if not texto_eli:
            texto_eli = (
                "Não consegui gerar uma resposta agora. "
                "Tenta novamente wy."
            )

        print("Resposta do Gemini recebida.")

        # =================================================
        # DETECTAR CÓDIGO
        # =================================================

        codigo = ""
        tipo = "js"

        if "```" in texto_eli:

            partes = texto_eli.split("```")

            if len(partes) >= 2:

                codigo_bruto = partes[1].strip()

                linhas = codigo_bruto.split("\n")

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

                        "python": "py",
                        "py": "py",

                        "json": "json",

                        "java": "java",

                        "c": "c",

                        "cpp": "cpp",
                        "c++": "cpp",

                        "php": "php",

                        "sql": "sql",

                        "typescript": "ts",
                        "ts": "ts"
                    }

                    if linguagem in linguagens:

                        tipo = linguagens[
                            linguagem
                        ]

                        codigo = "\n".join(
                            linhas[1:]
                        )

                    else:

                        codigo = codigo_bruto

        # =================================================
        # RESPOSTA
        # =================================================

        return jsonify({
            "resposta": texto_eli,
            "codigo": codigo,
            "tipo": tipo,
            "modelo": gemini_model
        })

    except Exception as e:

        erro = str(e)

        print(
            f"Erro Gemini: {erro}"
        )

        return jsonify({
            "resposta": (
                "❌ A Eli encontrou um erro temporário "
                "ao responder. Tenta novamente."
            ),
            "codigo": "",
            "tipo": "js",
            "erro": erro
        }), 500


# =========================================================
# INICIAR SERVIDOR
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
