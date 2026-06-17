// =======================
// ABRIR MENU
// =======================

function abrirMenu() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("hidden");
}


// =======================
// TROCAR TELAS (CORRIGIDO)
// =======================

function mostrar(id) {

  const telas = [
    "home",
    "login",
    "register",
    "editor",
    "linguagens",
    "apis",
    "banco",
    "projetos",
    "config"
  ];

  telas.forEach(t => {
    const el = document.getElementById(t);
    if (el) el.classList.add("hidden");
  });

  const target = document.getElementById(id);
  if (target) target.classList.remove("hidden");
}


// =======================
// INICIO
// =======================

window.onload = function () {
  mostrar("home");
};


// =======================
// LOGIN
// =======================

async function login() {

  const username = document.getElementById("user").value;
  const password = document.getElementById("pass").value;

  try {

    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    alert(data.msg);

    if (data.msg === "Login OK") {
      mostrar("editor");
    }

  } catch (e) {
    alert("Erro no login");
    console.log(e);
  }
}


// =======================
// REGISTER
// =======================

async function registrar() {

  const username = document.getElementById("new_user").value;
  const password = document.getElementById("new_pass").value;

  try {

    const res = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    alert(data.msg);

    if (data.msg.includes("sucesso")) {
      mostrar("login");
    }

  } catch (e) {
    alert("Erro no register");
    console.log(e);
  }
}


// =======================
// CHAT IA
// =======================

async function enviarMensagem() {

  const input = document.getElementById("iaInput");
  const texto = input.value.trim();
  const chat = document.getElementById("chatArea");

  if (!texto) return;

  chat.innerHTML += `<div class="msg-user">Tu: ${texto}</div>`;

  input.value = "";

  try {

    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensagem: texto })
    });

    const data = await res.json();

    chat.innerHTML += `<div class="msg-bot">IA: ${data.resposta}</div>`;

  } catch (e) {
    console.log(e);
    chat.innerHTML += `<div class="msg-bot">Erro na IA</div>`;
  }

  chat.scrollTop = chat.scrollHeight;
}


// =======================
// EXECUTAR CODIGO (SEGURO BÁSICO)
// =======================

function executar() {

  const codigo = document.getElementById("codigo").value;
  const consoleBox = document.getElementById("console");

  try {

    const resultado = Function('"use strict"; return (' + codigo + ')')();

    consoleBox.innerText = resultado || "Executado";

  } catch (e) {
    consoleBox.innerText = e;
  }
}


// =======================
// MENU SISTEMA
// =======================

function abrirLinguagens() {
  mostrar("linguagens");
}

function abrirApis() {
  mostrar("apis");
}

function abrirBanco() {
  mostrar("banco");
}

function abrirProjetos() {
  mostrar("projetos");
}

function abrirIA() {
  mostrar("editor");
}

function abrirTerminal() {
  mostrar("editor");
}

function abrirConfig() {
  mostrar("config");
}
