from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# HOME
@app.route("/")
def home():

    return render_template("index.html")

# LOGIN
@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if username and password:

            return jsonify({
                "msg": "Login OK"
            })

        else:

            return jsonify({
                "msg": "Preencha tudo"
            })

    except Exception as e:

        return jsonify({
            "msg": str(e)
        })

# REGISTER
@app.route("/register", methods=["POST"])
def register():

    try:

        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if username and password:

            return jsonify({
                "msg": "Conta criada com sucesso"
            })

        else:

            return jsonify({
                "msg": "Preencha tudo"
            })

    except Exception as e:

        return jsonify({
            "msg": str(e)
        })

# IA
@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        mensagem = data.get("mensagem")

        resposta = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",

                "Content-Type":
                "application/json"

            },

            json={

                "model":
                "mistralai/mistral-7b-instruct",

                "messages":[

                    {
                        "role":"system",

                        "content":
                        "Você é uma IA programadora tipo Replit."
                    },

                    {
                        "role":"user",

                        "content":mensagem
                    }

                ]

            }

        )

        resultado = resposta.json()

        # ERRO API
        if "error" in resultado:

            return jsonify({

                "resposta":
                "API sem saldo ou erro"

            })

        texto = resultado["choices"][0]["message"]["content"]

        return jsonify({

            "resposta":texto

        })

    except Exception as e:

        print(e)

        return jsonify({

            "resposta":
            "Erro servidor"

        })

# START
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(

        host="0.0.0.0",

        port=port

    )
