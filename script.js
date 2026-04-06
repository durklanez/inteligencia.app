const API = "https://inteligencia-apps.onrender.com";

// REGISTRO
async function registrar() {
  const username = document.getElementById("reg_user").value;
  const password = document.getElementById("reg_pass").value;

  const res = await fetch(API + "/register", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  alert(data.msg);
}

// LOGIN
async function login() {
  const username = document.getElementById("log_user").value;
  const password = document.getElementById("log_pass").value;

  const res = await fetch(API + "/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  alert(data.msg);
}

// GERAR APP
async function gerarApp() {
  const prompt = document.getElementById("prompt").value;

  const res = await fetch(API + "/gerar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ prompt })
  });

  const data = await res.json();
  document.getElementById("resultado").textContent = data.codigo;
}
