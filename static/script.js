<script>

// MENU
function abrirMenu(){
document.getElementById("sidebar")
.classList.toggle("hidden");
}

// TROCAR TELAS
function mostrar(id){

document.querySelectorAll(
"#home,#login,#register,#editor"
).forEach(div => div.classList.add("hidden"));

document.getElementById(id)
.classList.remove("hidden");

}

// INICIO
window.onload = () => {
mostrar("home");
}

// LOGIN
async function login(){

const username = document.getElementById("user").value;
const password = document.getElementById("pass").value;

const res = await fetch("/login",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
username,password
})
});

const data = await res.json();

alert(data.msg);

if(data.msg === "Login OK"){
mostrar("editor");
}

}

// REGISTER + LOGIN AUTOMÁTICO
async function registrar(){

const username = document.getElementById("new_user").value;
const password = document.getElementById("new_pass").value;

const res = await fetch("/register",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
username,password
})
});

const data = await res.json();

alert(data.msg);

if(data.msg.includes("sucesso")){

const loginRes = await fetch("/login",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
username,password
})
});

const loginData = await loginRes.json();

if(loginData.msg === "Login OK"){

mostrar("editor");

}

}

}

// IA
async function enviarMensagem(){

const texto = document.getElementById("iaInput").value;

if(!texto) return;

const chat = document.getElementById("chatArea");

chat.innerHTML += `
<div class="msg-user">
${texto}
</div>
`;

document.getElementById("iaInput").value = "";

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

chat.innerHTML += `
<div class="msg-bot">
${data.resposta}
</div>
`;

chat.scrollTop = chat.scrollHeight;

}

// RUN
function executar(){

try{

let result = eval(
document.getElementById("codigo").value
);

document.getElementById("console")
.innerHTML = result || "Executado com sucesso";

}catch(e){

document.getElementById("console")
.innerHTML = e;

}

}

</script>
