function mostrar(id) {
  document.querySelectorAll("#home, #login, #editor")
    .forEach(div => div.classList.add("hidden"));

  document.getElementById(id).classList.remove("hidden");
}

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

  if (data.msg === "Login OK") {
    mostrar("editor");
  } else {
    alert(data.msg);
  }
}

// CHAT IA REAL
async function enviarMensagem() {
  const input = document.getElementById("iaInput");
  const chat = document.getElementById("chatArea");

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

  chat.innerHTML += `<div style="text-align:left">${data.resposta}</div>`;
  chat.scrollTop = chat.scrollHeight;
}

// EXECUTAR
function executar() {
  const codigo = document.getElementById("codigo").value;

  try {
    let result = eval(codigo);
    document.getElementById("console").textContent = result || "OK";
  } catch (e) {
    document.getElementById("console").textContent = e;
  }
}
