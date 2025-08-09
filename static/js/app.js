// static/js/app.js
document.addEventListener("DOMContentLoaded", () => {
  const btnOpenTrans = document.getElementById("openTransmision");
  const btnOpenCapt = document.getElementById("openCaptura");
  if(btnOpenTrans){
    btnOpenTrans.addEventListener("click", ()=>{
      window.open("/transmision", "_blank", "toolbar=no,menubar=no,width=900,height=700");
    });
  }
  if(btnOpenCapt){
    btnOpenCapt.addEventListener("click", ()=>{
      window.open("/captura_autorizado", "_blank", "toolbar=no,menubar=no,width=900,height=700");
    });
  }

  function showToast(text, time=3500){
    const t = document.createElement("div");
    t.className = "toast";
    t.innerText = text;
    document.body.appendChild(t);
    setTimeout(()=> t.classList.add("visible"), 50);
    setTimeout(()=> { t.classList.remove("visible"); setTimeout(()=> t.remove(), 200); }, time);
  }

  const flashArea = document.querySelector(".flash-area");
  if(flashArea){
    const flashes = flashArea.querySelectorAll(".flash");
    flashes.forEach((el, idx) => {
      setTimeout(()=> showToast(el.innerText, 3500), idx * 400);
    });
  }
});