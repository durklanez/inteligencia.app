function abrirMenu(){

document.getElementById("sidebar")
.classList.toggle("hidden");

}

function mostrar(id){

document.querySelectorAll(
"#home,#login,#register,#editor"
).forEach(div => {

div.classList.add("hidden");

});

document.getElementById(id)
.classList.remove("hidden");

}

window.onload = function(){

mostrar("home");

}

function login(){

mostrar("editor");

}

function registrar(){

alert("Conta criada");

mostrar("editor");

}

function abrirPagina(id){

const paginas = [
"linguagens",
"apis",
"db",
"projetos",
"terminal",
"config"
];

paginas.forEach(p => {

document.getElementById(p)
.classList.add("hidden");

});

document.getElementById(id)
.classList.remove("hidden");

}

function addCodigo(tipo){

const codigo =
document.getElementById("codigo");

if(tipo === "python"){

codigo.value =
`print("Python OK")`;

}

if(tipo === "javascript"){

codigo.value =
`console.log("JS OK")`;

}

if(tipo === "html"){

codigo.value =
`<h1>HTML OK</h1>`;

}

if(tipo === "css"){

codigo.value =
`body{
background:black;
}`;

}

}

function testarAPI(){

alert("API funcionando");

}

function verDB(){

alert("Banco conectado");

}

function novoProjeto(){

document.getElementById("codigo")
.value = "";

}

function limparTerminal(){

document.getElementById("terminalBox")
.innerHTML = "Terminal limpo";

}

function temaDark(){

document.body.style.background =
"#000";

}

async function enviarMensagem(){

const texto =
document.getElementById("iaInput").value;

if(!texto) return;

const chat =
document.getElementById("chatArea");

chat.innerHTML += `
<div class="msg-user">
${texto}
</div>
`;

document.getElementById("iaInput").value = "";

chat.innerHTML += `
<div class="msg-bot">
IA respondeu: ${texto}
</div>
`;

chat.scrollTop = chat.scrollHeight;

}

function executar(){

try{

let codigo =
document.getElementById("codigo").value;

let result = eval(codigo);

document.getElementById("console")
.innerHTML = result || "Executado";

}catch(e){

document.getElementById("console")
.innerHTML = e;

}

}
