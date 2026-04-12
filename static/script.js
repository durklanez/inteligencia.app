// =========================
// NAVEGAÇÃO
// =========================
function mostrar(id) {
  document.querySelectorAll("#start, #aprendiz, #home, #login, #register, #menu, #ia")
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
// IA PROFISSIONAL
// =========================
async function gerar() {
  const prompt = document.getElementById("prompt").value;

  const res = await fetch("/gerar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({prompt})
  });

  const data = await res.json();
  document.getElementById("resultado").textContent = data.codigo;
}

// =========================
// IA APRENDIZ (SIMULAÇÃO)
// =========================
function responderIA() {
  const input = document.getElementById("chatInput").value.toLowerCase();
  let resposta = "";

  if (input.includes("programar")) {
    resposta = "Que tipo de programação quer aprender? (jogo, app ou site)";
  } else if (input.includes("jogo")) {
    resposta = "Boa! Para jogos simples, recomendo começar com JavaScript 🎮";
  } else if (input.includes("app")) {
    resposta = "Para apps, você pode usar Flutter ou React Native 📱";
  } else if (input.includes("site")) {
    resposta = "Para sites, comece com HTML, CSS e JavaScript 🌐";
  } else {
    resposta = "Explique melhor o que deseja aprender.";
  }

  document.getElementById("chatOutput").textContent = resposta;
}
