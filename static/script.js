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

  const telas = [
    "home",
    "login",
    "menu",
    "linguagens",
    "editor",
    "chat"
  ];

  telas.forEach(tela => {
    const el = document.getElementById(tela);

    if (el) {
      el.classList.add("hidden");
    }
  });

  const alvo = document.getElementById(id);

  if (alvo) {
    alvo.classList.remove("hidden");
  }
}

// =======================
// LOGIN
// =======================

function login() {

  const user = document.getElementById("user").value.trim();
  const pass = document.getElementById("pass").value.trim();

  if (!user || !pass) {
    alert("Preenche utilizador e senha.");
    return;
  }

  logado = true;

  document
    .getElementById("sidebar")
    .classList.remove("hidden");

  mostrar("menu");
}

// =======================
// LOGOUT
// =======================

function logout() {

  logado = false;

  document
    .getElementById("sidebar")
    .classList.add("hidden");

  mostrar("home");
}

// =======================
// MENU
// =======================

function mostrarCriarApp() {
  mostrar("linguagens");
}

function voltarMenu() {
  mostrar("menu");
}

function voltarLinguagens() {
  mostrar("linguagens");
}

// =======================
// ABRIR EDITOR
// =======================

function abrirEditor(lang) {

  linguagemAtual = lang;

  const titulo =
    document.getElementById("langTitle");

  const fileName =
    document.getElementById("fileName");

  titulo.innerText = "💻 " + lang;

  if (lang === "Python") {
    fileName.innerText = "📄 app.py";
  }

  if (lang === "JavaScript") {
    fileName.innerText = "📄 script.js";
  }

  if (lang === "HTML") {
    fileName.innerText = "📄 index.html";
  }

  if (lang === "CSS") {
    fileName.innerText = "📄 style.css";
  }

  const codigoSalvo =
    localStorage.getItem(
      "codigo_" + linguagemAtual
    );

  document.getElementById("codigo").value =
    codigoSalvo || "";

  mostrar("editor");
}

// =======================
// EXECUTAR
// =======================

function executar() {

  const codigo =
    document.getElementById("codigo").value;

  const consoleBox =
    document.getElementById("console");

  if (linguagemAtual !== "JavaScript") {

    consoleBox.innerText =
      "⚠️ Judge0 ainda não ligado.\n\n" +
      "A execução de " +
      linguagemAtual +
      " será ativada quando ligares o compilador.";

    return;
  }

  try {

    const resultado = eval(codigo);

    if (resultado === undefined) {
      consoleBox.innerText =
        "✅ Executado com sucesso";
    } else {
      consoleBox.innerText =
        String(resultado);
    }

  } catch (erro) {

    consoleBox.innerText =
      "❌ Erro:\n" + erro;

  }
}

// =======================
// GUARDAR CÓDIGO
// =======================

function salvarCodigo() {

  const codigo =
    document.getElementById("codigo").value;

  localStorage.setItem(
    "codigo_" + linguagemAtual,
    codigo
  );

  alert(
    "Código guardado em " +
    linguagemAtual
  );
}

// =======================
// ENVIAR CÓDIGO PARA IA
// =======================

function enviarCodigoIA() {

  const codigo =
    document.getElementById("codigo").value;

  if (!codigo) {
    alert("Escreve algum código primeiro.");
    return;
  }

  chatHistorico.push(
    "Tu: Analisa este código:\n" + codigo
  );

  chatHistorico.push(
    "IA: Recebi o código " +
    linguagemAtual +
    " para análise. 🤖"
  );

  mostrarChat();
}

// =======================
// CHAT IA
// =======================

function mostrarChat() {

  mostrar("chat");

  const box =
    document.getElementById("chatBox");

  box.innerHTML =
    chatHistorico
      .map(msg => `<div>${msg}</div>`)
      .join("");
}

// =======================
// ENVIAR MENSAGEM
// =======================

function enviarMsg() {

  const input =
    document.getElementById("msg");

  const texto =
    input.value.trim();

  if (!texto) {
    return;
  }

  chatHistorico.push(
    "Tu: " + texto
  );

  chatHistorico.push(
    "IA: Estou dentro do Intelligence App a ajudar-te. 🤖"
  );

  input.value = "";

  mostrarChat();
}

// =======================
// INICIAR APP
// =======================

window.onload = function () {

  document
    .getElementById("sidebar")
    .classList.add("hidden");

  mostrar("home");
};
