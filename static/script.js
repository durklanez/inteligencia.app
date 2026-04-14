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
// CHAT IA
// =========================
function responderIA() {
  const input = document.getElementById("chatInput").value;
  const chatBox = document.getElementById("chatBox");

  if (!input) return;

  chatBox.innerHTML += "<p><b>Você:</b> " + input + "</p>";

  let resposta = "Explica melhor o que quer aprender.";

  if (input.toLowerCase().includes("programar")) {
    resposta = "Quer aprender jogo, app ou site?";
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

// =========================
// IA DO EDITOR
// =========================
function perguntarIA() {
  const pergunta = document.getElementById("iaInput").value;
  const codigo = document.getElementById("codigo").value;

  let resposta = "Explique melhor o problema.";

  if (pergunta.toLowerCase().includes("erro")) {
    resposta = "Verifique a sintaxe do código.";
  } else if (codigo.includes("console.log")) {
    resposta = "Seu código parece correto 👍";
  }

  document.getElementById("iaResposta").textContent = resposta;
}
