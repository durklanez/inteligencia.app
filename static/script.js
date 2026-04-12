// =========================
// NAVEGAÇÃO
// =========================
function mostrar(id) {
  document.querySelectorAll("#home, #login, #register, #menu, #aprendiz, #linguagens, #editor")
    .forEach(div => div.classList.add("hidden"));

  document.getElementById(id).classList.remove("hidden");
}

// =========================
// LOGIN
// =========================
async function login() {
  const username = document.getElementById("user").value;
  const password = document.getElementById("pass").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });

  const data = await res.json();
  alert(data.msg);

  if (data.msg === "Login OK") {
    mostrar("menu");
  }
}

// =========================
// REGISTRAR
// =========================
async function registrar() {
  const username = document.getElementById("new_user").value;
  const password = document.getElementById("new_pass").value;

  const res = await fetch("/register", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });

  const data = await res.json();
  alert(data.msg);

  if (data.msg.includes("sucesso")) {
    mostrar("login");
  }
}

// =========================
// CHAT IA (APRENDIZ)
// =========================
function responderIA() {
  const input = document.getElementById("chatInput").value;
  const chatBox = document.getElementById("chatBox");

  if (!input) return;

  chatBox.innerHTML += "<p><b>Você:</b> " + input + "</p>";

  let resposta = "";
  const texto = input.toLowerCase();

  if (texto.includes("programar")) {
    resposta = "Quer aprender jogo, app ou site?";
  } else if (texto.includes("jogo")) {
    resposta = "Vamos usar JavaScript para jogos 🎮";
  } else if (texto.includes("app")) {
    resposta = "Use Flutter ou React Native 📱";
  } else if (texto.includes("site")) {
    resposta = "Aprende HTML, CSS e JS 🌐";
  } else {
    resposta = "Explica melhor o que quer aprender.";
  }

  chatBox.innerHTML += "<p><b>IA:</b> " + resposta + "</p>";

  document.getElementById("chatInput").value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
}

// =========================
// EDITOR
// =========================
function abrirEditor(lang) {
  document.getElementById("tituloLinguagem").textContent = "Editor - " + lang;
  mostrar("editor");
}

function executar() {
  const codigo = document.getElementById("codigo").value;

  try {
    let resultado = eval(codigo);
    document.getElementById("console").textContent = resultado || "Executado com sucesso";
  } catch (erro) {
    document.getElementById("console").textContent = "Erro: " + erro;
  }
}
