from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/gerar", methods=["POST"])
def gerar():
    data = request.get_json()
    prompt = data.get("prompt")

    # Simulação de IA (depois você liga com OpenAI)
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
        body: Center(child: Text("App gerado com IA 🚀")),
      ),
    );
  }}
}}
"""

    return jsonify({"codigo": codigo})

if __name__ == "__main__":
    app.run()
