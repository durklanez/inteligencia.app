import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: TestePage(),
    );
  }
}

class TestePage extends StatefulWidget {
  @override
  State<TestePage> createState() => _TestePageState();
}

class _TestePageState extends State<TestePage> {
  final String url = 'https://inteligencia-apps.onrender.com/teste-firestore';
  String resultado = "Clica no botão pra testar";

  Future<void> testarBackend() async {
    setState(() {resultado = "Enviando..."});
    final dados = {"nome": "Josue Teste", "email": "josue@teste.com", "idade": 22};
    try {
      final resposta = await http.post(
        Uri.parse(url),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(dados),
      );
      setState(() {resultado = "SUCESSO: ${resposta.body}"});
    } catch (e) {
      setState(() {resultado = "ERRO: $e"});
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Teste Backend")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: testarBackend,
              child: Text("TESTAR BACKEND"),
            ),
            SizedBox(height: 20),
            Text(resultado, textAlign: TextAlign.center)
          ],
        ),
      ),
    );
  }
}
