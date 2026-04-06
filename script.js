// URL do backend no Render
const API = "https://inteligencia-apps.onrender.com";

// =========================
// TROCAR TELAS
// =========================
function mostrar(tela) {
  document.querySelectorAll(".container > div").forEach(div => {
    div.classList.add("hidden");
  });
  document.getElementById(tela).classList.remove("hidden");
}

// =========================
// LOGIN
// =========================
async function login() {
  try {
    const username = document.getElementById("user").value.trim();
    const password = document.getElementById("pass").value.trim();

    if (!username || !password) {
      alert("Preencha usuário e senha!");
      return;
    }

    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (!res.ok) throw new Error("Erro ao conectar ao servidor");

    const data = await res.json();
    alert(data.msg);

    if (data.msg === "Login OK") {
      // Limpar campos
      document.getElementById("user").value = "";
      document.getElementById("pass").value = "";
      mostrar("menu");
    }
  } catch (err) {
    alert("Erro: " + err.message);
    console.error(err);
  }
}

// =========================
// REGISTRO
// =========================
async function registrar() {
  try {
    const username = document.getElementById("new_user").value.trim();
    const password = document.getElementById("new_pass").value.trim();

    if (!username || !password) {
      alert("Preencha usuário e senha!");
      return;
    }

    const res = await fetch(`${API}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (!res.ok) throw new Error("Erro ao conectar ao servidor");

    const data = await res.json();
    alert(data.msg);

    // Limpar campos
    document.getElementById("new_user").value = "";
    document.getElementById("new_pass").value = "";

    mostrar("login");
  } catch (err) {
    alert("Erro: " + err.message);
    console.error(err);
  }
}

// =========================
// GERAR APP COM IA
// =========================
async function gerar() {
  try {
    const prompt = document.getElementById("prompt").value.trim();

    if (!prompt) {
      alert("Digite algo para gerar o app!");
      return;
    }

    // Mensagem de loading
    document.getElementById("resultado").textContent = "Gerando app... 🚀";

    const res = await fetch(`${API}/gerar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    if (!res.ok) throw new Error("Erro ao conectar ao servidor");

    const data = await res.json();
    document.getElementById("resultado").textContent = data.codigo;
  } catch (err) {
    alert("Erro: " + err.message);
    console.error(err);
  }
}
