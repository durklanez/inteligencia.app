const API = "https://inteligencia-apps.onrender.com";

// TROCAR TELA
function mostrar(tela) {
  document.querySelectorAll(".container > div").forEach(div => {
    div.classList.add("hidden");
  });
  document.getElementById(tela).classList.remove("hidden");
}

// LOGIN
async function login() {
  const username = document.getElementById("user").value;
  const password = document.getElementById("pass").value;

  const res = await fetch(API + "/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  alert(data.msg);

  if (data.msg === "Login OK") {
    mostrar("menu");
  }
}

// REGISTRO
async function registrar() {
  const username = document.getElementById("new_user").value;
  const password = document.getElementById("new_pass").value;

  const res = await fetch(API + "/register", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  alert(data.msg);

  mostrar("login");
}

// GERAR APP
async function gerar() {
  const prompt = document.getElementById("prompt").value;

  const res = await fetch(API + "/gerar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ prompt })
  });

  const data = await res.json();
  document.getElementById("resultado").textContent = data.codigo;
}
