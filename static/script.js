function mostrar(id) {
  document.querySelectorAll("#home, #login, #register, #editor")
    .forEach(div => div.classList.add("hidden"));

  document.getElementById(id).classList.remove("hidden");
}

// inicia na home
window.onload = () => mostrar("home");

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
    mostrar("editor");
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

// IA
async function enviarMensagem() {
  const input = document.getElementById("iaInput");
  const chat = document.getElementById("chatArea");
  const codigo = document.getElementById("codigo");

  const texto = input.value;
  if (!texto) return;

  chat.innerHTML += `<div style="text-align:right">${texto}</div>`;
  input.value = "";

  const res = await fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({mensagem: texto})
  });

  const data = await res.json();

  chat.innerHTML += `<div style="text-align:left;color:#22c55e">${data.resposta}</div>`;

  // pega código automático
  const match = data.resposta.match(/```([\s\S]*?)```/);
  if (match) {
    codigo.value = match[1];
  }

  chat.scrollTop = chat.scrollHeight;
}

// EXECUTAR
function executar() {
  try {
    let result = eval(document.getElementById("codigo").value);
    document.getElementById("console").textContent = result || "Executado";
  } catch (e) {
    document.getElementById("console").textContent = e;
  }
}
