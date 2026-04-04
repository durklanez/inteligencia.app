from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Criar banco de dados
def criar_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

criar_db()

# REGISTRO
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Usuário criado com sucesso!"})

# LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({"msg": "Login OK"})
    else:
        return jsonify({"msg": "Credenciais inválidas"})

# GERAR APP (já tinha)
@app.route("/gerar", methods=["POST"])
def gerar():
    data = request.get_json()
    prompt = data.get("prompt")

    codigo = f"App criado: {prompt}"
    return jsonify({"codigo": codigo})

if __name__ == "__main__":
    app.run()
