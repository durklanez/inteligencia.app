
async function gerarApp() {
  const prompt = document.getElementById("prompt").value;

  const resposta = await fetch("https://teu-backend.onrender.com/gerar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ prompt })
  });

  const dados = await resposta.json();

  document.getElementById("resultado").textContent = dados.codigo;
}
