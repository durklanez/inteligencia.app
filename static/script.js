// NAVEGAÇÃO
function mostrar(id) {
  document.querySelectorAll("#home, #login, #register, #menu, #aprendiz, #linguagens, #editor")
    .forEach(div => div.classList.add("hidden"));

  document.getElementById(id).classList.remove("hidden");
}

// INÍCIO (IMPORTANTE)
window.onload = function() {
  mostrar("home");
}

// LOGIN
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

// REGISTRAR
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

// CHAT IA
function responderIA() {
  const input = document.getElementById("chatInput").value;
  const chatBox = document.getElementById("chatBox");

  chatBox.innerHTML += "<p><b>Você:</b> " + input + "</p>";
  chatBox.innerHTML += "<p><b>IA:</b> Vamos aprender programação 🚀</p>";

  document.getElementById("chatInput").value = "";
}

// ABRIR EDITOR
function abrirEditor(lang) {
  mostrar("editor");
}

// EXECUTAR CÓDIGO
function executar() {
  const codigo = document.getElementById("codigo").value;

  try {
    let resultado = eval(codigo);
    document.getElementById("console").textContent = resultado || "Executado";
  } catch (erro) {
    document.getElementById("console").textContent = "Erro: " + erro;
  }
}

// IA EDITOR
function perguntarIA() {
  const pergunta = document.getElementById("iaInput").value;

  let resposta = "Explique melhor.";

  if (pergunta.toLowerCase().includes("erro")) {
    resposta = "Pode ter erro de sintaxe.";
  }

  document.getElementById("iaResposta").textContent = resposta;
}
