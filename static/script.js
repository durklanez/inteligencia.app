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
