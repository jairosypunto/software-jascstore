/* =====================================================
   🔥 STORE.JS – JascEcommerce (FINAL PRO)
===================================================== */

console.log("🔥 STORE.JS CARGADO");

document.addEventListener("DOMContentLoaded", () => {
  initSwipers();

  /* =============================
     ABRIR VISTA RÁPIDA
  ============================= */
  document.body.addEventListener("click", e => {
    const btn = e.target.closest(".quick-view, .abrir-modal");
    if (!btn) return;

    e.preventDefault();

    const panel = document.getElementById("vistaRapidaPanel");
    const cont  = document.getElementById("contenidoProducto");
    const id    = btn.dataset.id;

    if (!panel || !cont || !id) return;

    panel.classList.remove("hidden");
    cont.innerHTML = `<p class="text-center py-4">Cargando producto...</p>`;

    fetch(`/store/vista-rapida/${id}/`)
      .then(res => res.text())
      .then(html => {
        cont.innerHTML = html;
        initVistaRapida(); // 🔥 CLAVE
      });
  });

  /* =============================
     CERRAR MODAL
  ============================= */
  document.body.addEventListener("click", e => {
    if (e.target.classList.contains("cerrar-panel")) {
      document.getElementById("vistaRapidaPanel")?.classList.add("hidden");
    }
  });
});

/* =====================================================
   🌀 SWIPERS
===================================================== */
function initSwipers() {
  if (document.querySelector(".bannerSwiper")) {
    new Swiper(".bannerSwiper", {
      loop: true,
      autoplay: { delay: 4000 },
      pagination: { el: ".swiper-pagination", clickable: true }
    });
  }

  if (document.querySelector(".mySwiper")) {
    new Swiper(".mySwiper", {
      slidesPerView: 4,
      spaceBetween: 20,
      loop: true,
      observer: true,
      observeParents: true,
      breakpoints: {
        0: { slidesPerView: 2 },
        768: { slidesPerView: 3 },
        1024: { slidesPerView: 4 }
      }
    });
  }
}

/* =====================================================
   🧠 VISTA RÁPIDA (GALERÍA + VARIANTES)
===================================================== */
function initVistaRapida() {
  console.log("✅ initVistaRapida");

  const cont = document.getElementById("contenidoProducto");
  if (!cont) return;

  /* =============================
     GALERÍA (IMÁGENES / VIDEO)
  ============================= */
  const visor = cont.querySelector(".imagen-principal");
  const minis = cont.querySelectorAll(".miniatura");

  minis.forEach(mini => {
    mini.addEventListener("click", () => {

      minis.forEach(m => m.classList.remove("activa"));
      mini.classList.add("activa");

      visor.innerHTML = "";

      const type = mini.dataset.type || "image";
      const src  = mini.dataset.src;

      if (type === "image") {
        const img = document.createElement("img");
        img.src = src;
        img.className = "big-image";
        visor.appendChild(img);
      }

      if (type === "video") {
        const video = document.createElement("video");
        video.src = src;
        video.controls = true;
        video.autoplay = true;
        video.className = "big-image";
        visor.appendChild(video);
      }
    });
  });

  /* =============================
     FORM CARRITO
  ============================= */
  const form = cont.querySelector("#form-add-cart");
  const btn  = form.querySelector("button");

  const hiddenTalla = cont.querySelector('[name="selected_size_hidden"]');
  const hiddenColor = cont.querySelector('[name="selected_color_hidden"]');

  const sizeChips  = cont.querySelectorAll(".size-chip");
  const colorChips = cont.querySelectorAll(".color-chip");

  let tallaOK = sizeChips.length === 0;   // ✔ Si no hay tallas → OK
  let colorOK = colorChips.length === 0;  // ✔ Si no hay colores → OK

  validar(); // 🔥 Evaluar al cargar

  /* =============================
     TALLAS
  ============================= */
  sizeChips.forEach(chip => {
    chip.addEventListener("click", () => {
      sizeChips.forEach(c => c.classList.remove("seleccionado"));
      chip.classList.add("seleccionado");

      hiddenTalla.value = chip.innerText.trim();
      tallaOK = true;
      validar();
    });
  });

  /* =============================
     COLORES
  ============================= */
  colorChips.forEach(chip => {
    chip.addEventListener("click", () => {
      colorChips.forEach(c => c.classList.remove("seleccionado"));
      chip.classList.add("seleccionado");

      hiddenColor.value = chip.innerText.trim();
      colorOK = true;
      validar();
    });
  });

  /* =============================
     VALIDACIÓN FINAL
  ============================= */
  function validar() {
    btn.disabled = !(tallaOK && colorOK);
  }
}
