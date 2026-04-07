from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # 🔥 Libera acesso do frontend

# =========================
# BANCO DE DADOS
# =========================
def criar_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

criar_db()

# =========================
# REGISTRO
# =========================
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"msg": "Erro: sem dados"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"msg": "Preencha todos os campos"}), 400

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({"msg": "Usuário já existe!"}), 400

        conn.close()

        print("Novo usuário:", username)

        return jsonify({"msg": "Usuário criado com sucesso!"})

    except Exception as e:
        print("ERRO REGISTER:", e)
        return jsonify({"msg": "Erro no servidor"}), 500


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"msg": "Erro: sem dados"}), 400

        username = data.get("username")
        password = data.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        conn.close()

        if user:
            print("Login OK:", username)
            return jsonify({"msg": "Login OK"})
        else:
            return jsonify({"msg": "Credenciais inválidas"})

    except Exception as e:
        print("ERRO LOGIN:", e)
        return jsonify({"msg": "Erro no servidor"}), 500


# =========================
# GERAR APP (IA SIMPLES)
# =========================
@app.route("/gerar", methods=["POST"])
def gerar():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"msg": "Erro: sem dados"}), 400

        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"msg": "Digite algo"}), 400

        codigo = f"""
// App Flutter básico
import 'package:flutter/material.dart';

void main() {{
  runApp(MyApp());
}}

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text("{prompt}")),
        body: Center(
          child: Text("App gerado com IA 🚀")
        ),
      ),
    );
  }}
}}
"""

        return jsonify({"codigo": codigo})

    except Exception as e:
        print("ERRO IA:", e)
        return jsonify({"msg": "Erro no servidor"}), 500


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "Servidor rodando 🚀"


# =========================
# RENDER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
