// =======================
// ESTADO LOGIN
// =======================

let logado = false;
let chatHistorico = [];

// =======================
// MOSTRAR TELAS
// =======================

function mostrar(id) {

  const telas = ["home","login","menu","linguagens","editor","chat"];

  telas.forEach(t => {
    const el = document.getElementById(t);
    if (el) el.classList.add("hidden");
  });

  const alvo = document.getElementById(id);
  if (alvo) alvo.classList.remove("hidden");
}


// =======================
// LOGIN (SIMPLES)
// =======================

function login() {

  const u = document.getElementById("user").value;
  const p = document.getElementById("pass").value;

  if (u && p) {

    logado = true;

    document.getElementById("sidebar").classList.remove("hidden");

    mostrar("menu");

  } else {
    alert("Preenche login");
  }
}


// =======================
// LOGOUT
// =======================

function logout() {

  logado = false;

  document.getElementById("sidebar").classList.add("hidden");

  mostrar("home");
}


// =======================
// MENU -> CRIAR APP
// =======================

function mostrarCriarApp() {
  mostrar("linguagens");
}


// =======================
// ESCOLHER LINGUAGEM
// =======================

function abrirEditor(lang) {

  document.getElementById("langTitle").innerText = lang;

  mostrar("editor");
}


// =======================
// VOLTAR
// =======================

function voltarMenu() {
  mostrar("menu");
}

function voltarLinguagens() {
  mostrar("linguagens");
}


// =======================
// EXECUTAR (JS BÁSICO)
// =======================

function executar() {

  const code = document.getElementById("codigo").value;
  const consoleBox = document.getElementById("console");

  try {
    const result = Function('"use strict"; return (' + code + ')')();
    consoleBox.innerText = result || "Executado";
  } catch (e) {
    consoleBox.innerText = e;
  }
}


// =======================
// SALVAR CÓDIGO (LOCAL)
// =======================

function salvarCodigo() {

  const code = document.getElementById("codigo").value;

  localStorage.setItem("codigo_salvo", code);

  alert("Código guardado!");
}


// =======================
// IA CHAT (COM HISTÓRICO)
// =======================

function mostrarChat() {
  mostrar("chat");

  const box = document.getElementById("chatBox");

  box.innerHTML = chatHistorico.map(m =>
    `<div>${m}</div>`
  ).join("");
}

function enviarMsg() {

  const input = document.getElementById("msg");
  const text = input.value;

  if (!text) return;

  chatHistorico.push("Tu: " + text);
  chatHistorico.push("IA: Estou dentro do Intelligence App a ajudar-te 🤖");

  input.value = "";

  mostrarChat();
}
