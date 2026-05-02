<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cafunfo App</title>

<style>
body {
  background:#0f172a;
  color:white;
  font-family:Arial;
}

.container {
  padding:15px;
}

.hidden {
  display:none;
}

.box {
  background:#1e293b;
  padding:10px;
  margin-top:15px;
  border-radius:10px;
}

.chat {
  height:250px;
  overflow:auto;
  background:#020617;
  padding:10px;
  border-radius:10px;
}

.row {
  display:flex;
  gap:5px;
}

input, textarea, button {
  width:100%;
  padding:10px;
  margin-top:10px;
}

textarea {
  height:120px;
}

.send {
  width:60px;
  background:#3b82f6;
}

.run {
  background:#22c55e;
}
</style>
</head>

<body>

<div class="container">

<!-- HOME -->
<div id="home">
  <h2>🔥 Cafunfo App</h2>
  <button onclick="mostrar('login')">Entrar</button>
  <button onclick="mostrar('register')">Criar Conta</button>
</div>

<!-- LOGIN -->
<div id="login" class="hidden">
  <h2>Login</h2>
  <input id="user" placeholder="Usuário">
  <input id="pass" type="password" placeholder="Senha">
  <button onclick="login()">Entrar</button>
  <button onclick="mostrar('home')">⬅ Voltar</button>
</div>

<!-- REGISTER -->
<div id="register" class="hidden">
  <h2>Criar Conta</h2>
  <input id="new_user" placeholder="Usuário">
  <input id="new_pass" type="password" placeholder="Senha">
  <button onclick="registrar()">Criar Conta</button>
  <button onclick="mostrar('home')">⬅ Voltar</button>
</div>

<!-- EDITOR -->
<div id="editor" class="hidden">

  <!-- CONSOLE -->
  <div class="box">
    <h3>💻 Console</h3>
    <div id="console">Pronto...</div>
  </div>

  <!-- IA -->
  <div class="box">
    <h3>🤖 IA</h3>

    <div id="chatArea" class="chat"></div>

    <div class="row">
      <input id="iaInput" placeholder="Fala com a IA...">
      <button class="send" onclick="enviarMensagem()">➤</button>
    </div>
  </div>

  <!-- CÓDIGO -->
  <div class="box">
    <h3>📄 Código</h3>
    <textarea id="codigo"></textarea>
    <button class="run" onclick="executar()">▶ Run</button>
  </div>

</div>

</div>

<script src="{{ url_for('static', filename='script.js') }}"></script>

</body>
</html>
