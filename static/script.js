// =======================
// MENU SISTEMA
// =======================

function abrirLinguagens(){

mostrar("editor");

document.getElementById("console").innerHTML = `
<h3>➕ Linguagens</h3>

✅ Python<br>
✅ JavaScript<br>
✅ HTML<br>
✅ CSS<br>
✅ Java<br>
✅ C++<br>
✅ PHP
`;

document.getElementById("codigo").value =
`# Escolha uma linguagem

print("Olá Mundo")`;

}

function abrirApis(){

mostrar("editor");

document.getElementById("console").innerHTML = `
<h3>🔑 APIs</h3>

Groq API<br>
OpenAI API<br>
Gemini API<br>
Firebase API<br>

Pronto para integração.
`;

}

function abrirBanco(){

mostrar("editor");

document.getElementById("console").innerHTML = `
<h3>🗄 Banco de Dados</h3>

✅ Firestore

Coleções:
- users
- projetos

Sistema conectado.
`;

}

function abrirProjetos(){

mostrar("editor");

document.getElementById("console").innerHTML = `
<h3>📁 Projetos</h3>

Novo Projeto

Salvar Projeto

Abrir Projeto

Importar Projeto
`;

}

function abrirIA(){

mostrar("editor");

document.getElementById("console").innerHTML = `
<h3>🤖 Inteligência Artificial</h3>

Chat IA ativo.

Faça perguntas no painel da IA.
`;

}

function abrirTerminal(){

mostrar("editor");

document.getElementById("console").innerHTML = `
<h3>🛠 Terminal</h3>

Terminal iniciado...

Digite JavaScript no editor e clique Run.
`;

}

function abrirConfig(){

mostrar("editor");

document.getElementById("console").innerHTML = `
<h3>⚡ Configurações</h3>

Tema Escuro

Conta

Segurança

Sistema
`;

}
