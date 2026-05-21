// =======================
// ABRIR MENU
// =======================

function abrirMenu(){

const sidebar =
document.getElementById("sidebar");

sidebar.classList.toggle("hidden");

}

// =======================
// TROCAR TELAS
// =======================

function mostrar(id){

document.querySelectorAll(
"#home,#login,#register,#editor"
).forEach(div => {

div.classList.add("hidden");

});

document.getElementById(id)
.classList.remove("hidden");

}

// =======================
// INICIO
// =======================

window.onload = function(){

mostrar("home");

}

// =======================
// LOGIN
// =======================

async function login(){

const username =
document.getElementById("user").value;

const password =
document.getElementById("pass").value;

try{

const res = await fetch("/login",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
username:username,
password:password
})

});

const data = await res.json();

alert(data.msg);

if(data.msg === "Login OK"){

mostrar("editor");

}

}catch(e){

alert("Erro no login");

console.log(e);

}

}

// =======================
// REGISTER
// =======================

async function registrar(){

const username =
document.getElementById("new_user").value;

const password =
document.getElementById("new_pass").value;

try{

const res = await fetch("/register",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
username:username,
password:password
})

});

const data = await res.json();

alert(data.msg);

if(data.msg.includes("sucesso")){

mostrar("editor");

}

}catch(e){

alert("Erro no register");

console.log(e);

}

}

// =======================
// CHAT IA
// =======================

async function enviarMensagem(){

const texto =
document.getElementById("iaInput").value;

if(!texto) return;

const chat =
document.getElementById("chatArea");

// MOSTRAR MENSAGEM USUARIO

chat.innerHTML += `
<div class="msg-user">
${texto}
</div>
`;

// LIMPAR INPUT

document.getElementById("iaInput").value = "";

try{

const res = await fetch("/chat",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
mensagem:texto
})

});

const data = await res.json();

console.log(data);

// MOSTRAR RESPOSTA IA

chat.innerHTML += `
<div class="msg-bot">
${data.resposta}
</div>
`;

}catch(e){

console.log(e);

chat.innerHTML += `
<div class="msg-bot">
Erro na IA
</div>
`;

}

// DESCER CHAT

chat.scrollTop = chat.scrollHeight;

}

// =======================
// EXECUTAR CODIGO
// =======================

function executar(){

try{

let codigo =
document.getElementById("codigo").value;

let resultado = eval(codigo);

document.getElementById("console")
.innerHTML = resultado || "Executado";

}catch(e){

document.getElementById("console")
.innerHTML = e;

}

}
