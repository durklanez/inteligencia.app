function mostrar(id) {
  document.querySelectorAll("#login, #editor")
    .forEach(div => div.classList.add("hidden"));

  document.getElementById(id).classList.remove("hidden");
}

window.onload = () => mostrar("login");

// LOGIN
async function login() {
  const username = user.value;
  const password = pass.value;

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

// IA
async function enviarMensagem() {
  const input = iaInput;
  const chat = chatArea;
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
  let resposta = data.resposta;

  chat.innerHTML += `<div style="text-align:left;color:#22c55e">${resposta}</div>`;

  // 🔥 PEGA CÓDIGO
  const match = resposta.match(/```([\s\S]*?)```/);

  if (match) {
    codigo.value = match[1];
  }

  chat.scrollTop = chat.scrollHeight;
}

// RUN
function executar() {
  try {
    let result = eval(codigo.value);
    console.textContent = result || "Executado";
  } catch (e) {
    console.textContent = e;
  }
}
