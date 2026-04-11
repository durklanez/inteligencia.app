from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

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
# HOME (AGORA MOSTRA HTML)
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# REGISTRO
# =========================
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"msg": "Usuário criado com sucesso!"})
    except:
        return jsonify({"msg": "Usuário já existe!"})

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    if user:
        return jsonify({"msg": "Login OK"})
    else:
        return jsonify({"msg": "Credenciais inválidas"})

# =========================
# IA
# =========================
@app.route("/gerar", methods=["POST"])
def gerar():
    data = request.get_json()
    prompt = data.get("prompt")

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

# =========================
# RENDER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
