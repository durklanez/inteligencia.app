// IA APRENDIZ (simples por agora)
function responderIA() {
  const input = document.getElementById("chatInput").value;
  let resposta = "";

  if (input.toLowerCase().includes("programar")) {
    resposta = "Que tipo de programação quer aprender? (jogo, app ou site)";
  } else if (input.toLowerCase().includes("jogo")) {
    resposta = "Boa! Vamos começar com JavaScript para jogos simples 🎮";
  } else {
    resposta = "Explique melhor o que deseja aprender.";
  }

  document.getElementById("chatOutput").textContent = resposta;
}
