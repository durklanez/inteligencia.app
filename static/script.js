function mostrar(id){
    const telas = ["home","login","register","menu"];

    telas.forEach(t => {
        document.getElementById(t).classList.add("hidden");
    });

    document.getElementById(id).classList.remove("hidden");
}

// =========================
// REGISTER
// =========================
async function criarConta(){
    const username = document.getElementById("newUser").value;
    const password = document.getElementById("newPass").value;

    const res = await fetch("/register",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username,password})
    });

    const data = await res.json();
    alert(data.msg);

    if(data.msg.includes("sucesso")){
        mostrar("login");
    }
}

// =========================
// LOGIN
// =========================
async function login(){
    const username = document.getElementById("user").value;
    const password = document.getElementById("pass").value;

    const res = await fetch("/login",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username,password})
    });

    const data = await res.json();
    alert(data.msg);

    if(data.msg.includes("sucesso")){
        localStorage.setItem("user", username);
        document.getElementById("welcome").innerText = "Bem-vindo " + username;
        mostrar("menu");
    }
}

// =========================
// LOGOUT
// =========================
function logout(){
    localStorage.removeItem("user");
    mostrar("home");
}
