function mostrar(id) {
  document.querySelectorAll("#home, #login, #register, #menu, #ia")
    .forEach(div => div.classList.add("hidden"));

  document.getElementById(id).classList.remove("hidden");
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

// IA
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
