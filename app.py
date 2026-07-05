import os
import json
from flask import Flask, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# FIREBASE
firebase_key_str = os.getenv("FIREBASE_KEY")
if firebase_key_str:
    cred_dict = json.loads(firebase_key_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

# ESSA É A LINHA MÁGICA WY - SERVE O HTML
@app.route("/")
def serve_frontend():
    return send_from_directory('.', 'index.html')

# SUA API
@app.route("/teste-firestore", methods=["GET", "POST"])
def teste():
    if request.method == "POST":
        data = request.get_json()
        return jsonify({"resposta": f"Eli recebeu: {data.get('pergunta')}"})
    return jsonify({"firebase":"OK","status":"API no ar wy 🚀"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
