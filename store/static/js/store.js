console.log("🔥 STORE.JS CARGADO");

/* =====================================================
   INIT
===================================================== */
document.addEventListener("DOMContentLoaded", () => {
  initEventosGlobales();
  initSliders();
  initHoverVideoEnGrid(); // 🆕 Hover video en tarjetas de productos
});

/* =====================================================
   EVENTOS GLOBALES
===================================================== */
function initEventosGlobales() {
  document.body.addEventListener("click", (e) => {

    /* ===== ABRIR VISTA RÁPIDA ===== */
    const btnQuick = e.target.closest(".quick-view");
    if (btnQuick) {
      e.preventDefault();
      const id = btnQuick.dataset.id;
      if (!id) {
        console.warn("⚠️ Botón sin data-id");
        return;
      }
      abrirVistaRapida(id);
      return;
    }

    /* ===== AGREGAR AL CARRITO DESDE GRID ===== */
    const btnCart = e.target.closest(".jasc-cart");
    if (btnCart) {
      e.preventDefault();
      const id = btnCart.dataset.id;

      if (!id) {
        console.warn("⚠️ Botón carrito sin data-id");
        return;
      }

      // ✅ Siempre abrir vista rápida como Temu
      console.log("🛍️ Abriendo vista rápida desde botón de carrito");
      abrirVistaRapida(id);
      return;
    }

    /* ===== CERRAR MODAL ===== */
    if (e.target.classList.contains("cerrar-panel")) {
      cerrarVistaRapida();
    }
  });
}

/* =====================================================
   ABRIR VISTA RÁPIDA
===================================================== */
function abrirVistaRapida(id) {
  const panel = document.getElementById("vistaRapidaPanel");
  const cont  = document.getElementById("contenidoProducto");

  panel.classList.remove("hidden");
  panel.classList.add("visible");
  document.body.style.overflow = "hidden";

  cont.innerHTML = "<p>Cargando producto...</p>";

  fetch(`/store/vista-rapida/${id}/`)
    .then(res => res.text())
    .then(html => {
      cont.innerHTML = html;
      setTimeout(initVistaRapida, 0);
    })
    .catch(err => {
      console.error("❌ Error cargando vista rápida", err);
      cont.innerHTML = "<p>Error cargando producto</p>";
    });
}

/* =====================================================
   CERRAR VISTA RÁPIDA
===================================================== */
function cerrarVistaRapida() {
  const panel = document.getElementById("vistaRapidaPanel");
  const cont  = document.getElementById("contenidoProducto");

  panel.classList.remove("visible");
  panel.classList.add("hidden");

  document.body.style.overflow = "";
  cont.innerHTML = "";

  console.log("❌ Vista rápida cerrada");
}

/* =====================================================
   LÓGICA VISTA RÁPIDA (IMÁGENES + VIDEO + CARRITO)
===================================================== */
function initVistaRapida() {
  const cont = document.getElementById("contenidoProducto");
  if (!cont) return;

  const visor = cont.querySelector("#visor-principal");
  const minis = cont.querySelectorAll(".miniatura");

  console.log(`📸 Miniaturas encontradas: ${minis.length}`);

  if (!visor || minis.length === 0) {
    console.warn("⚠️ No hay visor o miniaturas");
    return;
  }

  function activarMiniatura(mini) {
    minis.forEach(m => m.classList.remove("activa"));
    mini.classList.add("activa");
    visor.innerHTML = "";

    const type   = mini.dataset.type;
    const src    = mini.dataset.src;
    const poster = mini.dataset.poster || "";

    if (!src) {
      console.warn("⚠️ Miniatura sin data-src");
      return;
    }

    if (type === "image") {
      const img = document.createElement("img");
      img.src = src;
      img.className = "big-image";
      img.loading = "eager";
      img.alt = "Imagen del producto";
      visor.appendChild(img);
    }

    if (type === "video") {
      const video = document.createElement("video");
      video.src = src;
      if (poster) video.poster = poster;
      video.controls = true;
      video.autoplay = true;
      video.loop = true;
      video.muted = true;
      video.playsInline = true;
      video.className = "big-image";
      visor.appendChild(video);
      video.play().catch(() => {
        console.warn("⚠️ Autoplay bloqueado");
      });
    }
  }

  minis.forEach(mini => {
    mini.addEventListener("mouseover", () => activarMiniatura(mini));
    mini.addEventListener("click", () => activarMiniatura(mini));
  });
  activarMiniatura(minis[0]);

  /* =================================================
     TALLAS Y COLORES
  ================================================= */
  const form = cont.querySelector("#form-add-cart");
  if (!form) return;

  const btnAgregar = form.querySelector(".btn-agregar");
  const btnComprar = form.querySelector(".btn-comprar");

  const tallaHidden = form.querySelector('[name="selected_size_hidden"]');
  const colorHidden = form.querySelector('[name="selected_color_hidden"]');

  const tallas  = cont.querySelectorAll(".size-chip");
  const colores = cont.querySelectorAll(".color-chip");

  console.log(`🎨 Tallas: ${tallas.length} | Colores: ${colores.length}`);

  let tallaOK = tallas.length === 0;
  let colorOK = colores.length === 0;

  function validar() {
    if (btnAgregar) btnAgregar.disabled = !(tallaOK && colorOK);
    if (btnComprar) btnComprar.disabled = !(tallaOK && colorOK);
  }

  tallas.forEach(t => {
    t.addEventListener("click", () => {
      tallas.forEach(x => x.classList.remove("seleccionado"));
      t.classList.add("seleccionado");
      if (tallaHidden) tallaHidden.value = t.innerText.trim();
      tallaOK = true;
      validar();
    });
  });

  colores.forEach(c => {
    c.addEventListener("click", () => {
      colores.forEach(x => x.classList.remove("seleccionado"));
      c.classList.add("seleccionado");
      if (colorHidden) colorHidden.value = c.innerText.trim();
      colorOK = true;
      validar();
    });
  });

  validar();

  /* =================================================
     BOTÓN COMPRAR AHORA
  ================================================= */
  if (btnComprar) {
    btnComprar.addEventListener("click", () => {
      if (!(tallaOK && colorOK)) {
        alert("Selecciona talla y color antes de comprar");
        return;
      }
      window.location.href = `/store/checkout/${form.dataset.productId || ""}`;
    });
  }
}

/* =====================================================
   🛒 JascEcommerce – Agregar al carrito desde grid
===================================================== */
function agregarAlCarritoDirecto(id) {
  console.log("➡️ [JascEcommerce] Intentando agregar producto con ID:", id);

  fetch(`/store/agregar/${id}/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCSRFToken() }
  })
    .then(res => {
      if (!res.ok) throw new Error(`Error HTTP ${res.status}`);
      return res.json();
    })
    .then(data => {
      console.log("🛒 [JascEcommerce] Producto agregado:", data);
      mostrarToast("Producto agregado al carrito en JascEcommerce ✅");
      actualizarContadorCarrito(data.cart_count);

      // ✅ Redirigir al carrito después de agregar
      window.location.href = "/store/ver-carrito/";
    })
    .catch(err => {
      console.error("❌ [JascEcommerce] Error agregando al carrito", err);
      mostrarToast("Error al agregar producto en JascEcommerce ❌");
    });
}

/* =====================================================
   UTILIDADES
===================================================== */
function getCSRFToken() {
  const cookie = document.cookie.split(";").find(c => c.trim().startsWith("csrftoken="));
  return cookie ? cookie.split("=")[1] : "";
}

function mostrarToast(msg) {
  const toast = document.createElement("div");
  toast.className = "toast-carrito";
  toast.innerText = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add("visible"), 50);
  setTimeout(() => {
    toast.classList.remove("visible");
    toast.remove();
  }, 3000);
}

function actualizarContadorCarrito(count) {
  const badge = document.querySelector(".cart-count");
  if (badge) badge.innerText = count;
}

/* =====================================================
   HOVER VIDEO EN GRID DE PRODUCTOS
===================================================== */
function initHoverVideoEnGrid() {
  const cards = document.querySelectorAll(".product-card .product-image-wrapper");
  if (!cards.length) return;

  cards.forEach(wrapper => {
    const img = wrapper.querySelector("img.product-img");
    if (!img) return;

    const videoSrc = wrapper.dataset.videoSrc;
    const videoPoster = wrapper.dataset.videoPoster;
    if (!videoSrc) return; // solo si el producto tiene video

    let videoEl = null;

    function activarVideo() {
      if (videoEl) return; // evitar múltiples instancias

      videoEl = document.createElement("video");
      videoEl.src = videoSrc;
      if (videoPoster) videoEl.poster = videoPoster;
      videoEl.autoplay = true;
      videoEl.muted = true;
      videoEl.loop = true;
      videoEl.playsInline = true;
      videoEl.className = "product-video";

      // estilos similares a la imagen
      videoEl.style.width = "100%";
      videoEl.style.height = "100%";
      videoEl.style.objectFit = "cover";
      videoEl.style.borderRadius = getComputedStyle(img).borderRadius;

      wrapper.appendChild(videoEl);

      videoEl.play().catch(() => {
        console.warn("⚠️ Autoplay bloqueado en grid");
      });
    }

    function desactivarVideo() {
      if (!videoEl) return;
      try { videoEl.pause(); } catch(e) {}
      videoEl.remove();
      videoEl = null;
    }

    // Hover en desktop, focus/blur para accesibilidad
    wrapper.addEventListener("mouseenter", activarVideo);
    wrapper.addEventListener("mouseleave", desactivarVideo);
    wrapper.addEventListener("focusin", activarVideo);
    wrapper.addEventListener("focusout", desactivarVideo);
  });
}

/* =====================================================
   SLIDERS (SWIPER)
===================================================== */
function initSliders() {
  if (typeof Swiper === "undefined") {
    console.warn("⚠️ Swiper no cargado");
    return;
  }

  // Banner principal
  new Swiper(".bannerSwiper", {
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false // ✅ sigue moviéndose aunque el usuario haga click o swipe
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev"
    }
  });

  // Productos destacados
  new Swiper(".destacados-swiper", {
    slidesPerView: 1.2,
    spaceBetween: 15,
    breakpoints: {
      768: { slidesPerView: 3 },
      1200: { slidesPerView: 5 }
    },
    autoplay: {
      delay: 4000,
      disableOnInteraction: false // ✅ se mueve solo y no se detiene
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev"
    }
  });

  console.log("🎞 Sliders inicializados");
}
