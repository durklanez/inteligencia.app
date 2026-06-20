// =======================
// ESTADO GLOBAL
// =======================

let logado = false;
let chatHistorico = [];
let linguagemAtual = "Python";


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
// ESCOLHER LINGUAGEM + EDITOR
// =======================

function abrirEditor(lang) {

  linguagemAtual = lang;

  document.getElementById("langTitle").innerText = "💻 " + lang;

  const fileName = document.getElementById("fileName");

  if (lang === "Python") fileName.innerText = "📄 app.py";
  if (lang === "JavaScript") fileName.innerText = "📄 script.js";
  if (lang === "HTML") fileName.innerText = "📄 index.html";
  if (lang === "CSS") fileName.innerText = "📄 style.css";

  // carregar código salvo
  const saved = localStorage.getItem("codigo_" + linguagemAtual);
  if (saved) {
    document.getElementById("codigo").value = saved;
  } else {
    document.getElementById("codigo").value = "";
  }

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
// EXECUTAR CÓDIGO
// =======================

function executar() {

  const code = document.getElementById("codigo").value;
  const consoleBox = document.getElementById("console");

  if (linguagemAtual !== "JavaScript") {
    consoleBox.innerText =
      "⚠️ Execução disponível apenas para JavaScript (Judge0 ainda não ligado)\n" +
      "Linguagem atual: " + linguagemAtual;
    return;
  }

  try {
    const result = Function('"use strict"; return (' + code + ')')();
    consoleBox.innerText = result || "Executado com sucesso";
  } catch (e) {
    consoleBox.innerText = "Erro: " + e.message;
  }
}


// =======================
// SALVAR CÓDIGO (POR LINGUAGEM)
// =======================

function salvarCodigo() {

  const code = document.getElementById("codigo").value;

  localStorage.setItem("codigo_" + linguagemAtual, code);

  alert("Código guardado em " + linguagemAtual + "!");
}


// =======================
// ENVIAR PARA IA
// =======================

function enviarCodigoIA() {

  const codigo = document.getElementById("codigo").value;

  if (!codigo) return;

  chatHistorico.push("Tu: Analisa este código:\n" + codigo);

  chatHistorico.push("IA: Recebi o código da linguagem " + linguagemAtual + ". Vou analisar... 🤖");

  mostrarChat();
}


// =======================
// CHAT IA
// =======================

function mostrarChat() {

  mostrar("chat");

  const box = document.getElementById("chatBox");

  box.innerHTML = chatHistorico.map(m =>
    `<div class="msg">${m}</div>`
  ).join("");
}


// enviar mensagem normal
function enviarMsg() {

  const input = document.getElementById("msg");
  const text = input.value.trim();

  if (!text) return;

  chatHistorico.push("Tu: " + text);
  chatHistorico.push("IA: Estou dentro do Intelligence App a responder 🤖");

  input.value = "";

  mostrarChat();
}
