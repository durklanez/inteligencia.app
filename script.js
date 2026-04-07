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
  try {
    const username = document.getElementById("user").value;
    const password = document.getElementById("pass").value;

    console.log("Tentando login:", username, password);

    const res = await fetch(API + "/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ username, password })
    });

    console.log("Resposta status:", res.status);

    const data = await res.json();
    console.log("Resposta backend:", data);

    alert(data.msg);

    if (data.msg === "Login OK") {
      mostrar("menu");
    }

  } catch (erro) {
    console.error("ERRO LOGIN:", erro);
    alert("Erro ao conectar ao servidor");
  }
}

// REGISTRO
async function registrar() {
  try {
    const username = document.getElementById("new_user").value;
    const password = document.getElementById("new_pass").value;

    console.log("Registrando:", username, password);

    const res = await fetch(API + "/register", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ username, password })
    });

    console.log("Resposta status:", res.status);

    const data = await res.json();
    console.log("Resposta backend:", data);

    alert(data.msg);

    mostrar("login");

  } catch (erro) {
    console.error("ERRO REGISTRO:", erro);
    alert("Erro ao conectar ao servidor");
  }
}

// GERAR
async function gerar() {
  try {
    const prompt = document.getElementById("prompt").value;

    document.getElementById("resultado").textContent = "Gerando...";

    const res = await fetch(API + "/gerar", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ prompt })
    });

    const data = await res.json();
    document.getElementById("resultado").textContent = data.codigo;

  } catch (erro) {
    console.error("ERRO IA:", erro);
    alert("Erro ao gerar app");
  }
}
