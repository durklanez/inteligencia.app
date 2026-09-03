async function enviar(){

  // Impede duas requisições ao mesmo tempo
  if(enviando) return;

  let p =
    document.getElementById('perg');

  if(!p || !p.value.trim()) return;

  enviando = true;

  let pergunta =
    p.value;

  addMsg(
    pergunta,
    'user'
  );

  historico.push({
    role:"user",
    content:pergunta
  });

  p.value = "";

  let loadingId =
    addMsg(
      "Eli pensando...",
      "eli"
    );


  try{

    let res =
      await fetch(
        "/teste-firestore",
        {
          method:"POST",

          headers:{
            "Content-Type":
              "application/json",
            "Accept":
              "application/json"
          },

          body:JSON.stringify({
            pergunta,
            historico
          })
        }
      );


    if(!res.ok){

      let erroTexto =
        await res.text();

      console.error(
        "Resposta do servidor:",
        erroTexto
      );

      throw new Error(
        "Servidor " +
        res.status
      );

    }


    let textoResposta =
      await res.text();


    let data;

    try{

      data =
        JSON.parse(textoResposta);

    }catch(jsonError){

      console.error(
        "Resposta recebida:",
        textoResposta
      );

      throw new Error(
        "O servidor não respondeu corretamente. Tenta novamente."
      );

    }


    let loading =
      document.getElementById(loadingId);

    if(loading){
      loading.remove();
    }


    if(data.resposta){

      historico.push({
        role:"assistant",
        content:data.resposta
      });

    }


    let html =
      `<div class="msg eli">${data.resposta || "Sem resposta."}`;


    /*
     * CÓDIGO
     */

    if(data.codigo){

      ultimoCod =
        data.codigo;

      ultimoTipo =
        data.tipo || "js";


      if(!(ultimoTipo in arquivos)){

        html +=
          `<div class="aviso">
          ⚠️ Wy, tá faltando a aba ${ultimoTipo.toUpperCase()}<br>
          Vai no menu ⋮ e clica em "Adicionar ${ultimoTipo.toUpperCase()}"
          </div>`;

      }


      html +=
        `<br>
        <button class="btn2"
        onclick="enviarEditor()">
        📤 Enviar pro Editor
        </button>`;

    }


    html +=
      `</div>`;


    document
      .getElementById('msgs')
      .innerHTML += html;


    document
      .getElementById('msgs')
      .scrollTop = 9999;


  }catch(e){

    let loading =
      document.getElementById(loadingId);

    if(loading){
      loading.remove();
    }

    addMsg(
      "❌ " + e.message,
      "eli"
    );

    console.error(
      "Erro Eli:",
      e
    );

  }finally{

    enviando = false;

  }

}
