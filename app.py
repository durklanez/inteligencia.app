from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from google import genai
from google.genai import types

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# Configuração do Gemini
api_key = os.environ.get("GEMINI_API_KEY")
gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

client = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Gemini inicializado com sucesso.")
    except Exception as e:
        print("ERRO AO INICIALIZAR GEMINI:", repr(e))
else:
    print("ERRO: GEMINI_API_KEY não encontrada.")


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/teste")
def teste():
    return jsonify({
        "status": "online",
        "gemini": client is not None,
        "modelo": gemini_model,
        "firebase": False
    })


@app.route("/teste-firestore", methods=["POST", "OPTIONS"])
def teste_firestore():

    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            data = {}

        pergunta = str(data.get("pergunta", "")).strip()
        historico = data.get("historico", [])

        if not pergunta:
            return jsonify({
                "resposta": "Digite uma mensagem para a Eli.",
                "codigo": "",
                "tipo": "js"
            })

        if client is None:
            return jsonify({
                "resposta": "❌ GEMINI_API_KEY não está configurada no Render.",
                "codigo": "",
                "tipo": "js"
            }), 500

        contents = []

        if isinstance(historico, list):

            for msg in historico[-10:]:

                if not isinstance(msg, dict):
                    continue

                texto = msg.get("content")

                if not texto:
                    continue

                texto = str(texto)

                role = msg.get("role", "user")

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

        # Evita duplicar a pergunta atual.
        if not contents or contents[-1]["role"] != "user" or contents[-1]["parts"][0]["text"] != pergunta:
            contents.append({
                "role": "user",
                "parts": [
                    {
                        "text": pergunta
                    }
                ]
            })

        print("========================================")
        print("PERGUNTA:", pergunta)
        print("MODELO:", gemini_model)
        print("========================================")

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
                temperature=0.7
            )
        )

        resposta = response.text

        if not resposta:
            resposta = "Não consegui gerar uma resposta agora."

        print("GEMINI RESPONDEU COM SUCESSO.")

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
                    codigo = "\n".join(linhas[1:])
                else:
                    codigo = bloco

        return jsonify({
            "resposta": resposta,
            "codigo": codigo,
            "tipo": tipo,
            "modelo": gemini_model
        })

    except Exception as e:

        erro = repr(e)

        print("========================================")
        print("ERRO REAL DO GEMINI/SERVIDOR:")
        print(erro)
        print("========================================")

        return jsonify({
            "resposta": "❌ Erro no servidor. Verifica os logs do Render.",
            "codigo": "",
            "tipo": "js",
            "erro": erro
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port
    )
