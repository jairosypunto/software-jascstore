console.log("🔥 STORE.JS CARGADO - Modo Sincronización Temu PRO Full");

/* =====================================================
    INIT & CONFIGURACIÓN GLOBAL
===================================================== */
document.addEventListener("DOMContentLoaded", () => {
    initEventosGlobales();
    initSliders(); // El slider de destacados se inicializa aquí
    initHoverVideoEnGrid();
    inicializarCarritoModal();
});

function getCSRFToken() { 
    return document.cookie.split(";").find(c => c.trim().startsWith("csrftoken="))?.split("=")[1] || ""; 
}

function mostrarToast(msg) {
    const toastsPrevios = document.querySelectorAll(".toast-carrito");
    toastsPrevios.forEach(t => t.remove());

    const t = document.createElement("div");
    t.className = "toast-carrito visible";
    t.innerText = msg;
    document.body.appendChild(t);
    setTimeout(() => {
        t.style.opacity = "0";
        setTimeout(() => t.remove(), 500);
    }, 3000);
}

/* =====================================================
    GESTIÓN DEL SIDE CART (CARRITO LATERAL TIPO TEMU)
===================================================== */
function abrirSideCart() {
    const cart = document.getElementById("sideCart");
    const overlay = document.getElementById("sideCartOverlay");
    if (cart && overlay) {
        cart.classList.add("visible");
        overlay.style.display = "block";
        document.body.style.overflow = "hidden";
    }
}

function cerrarSideCart() {
    const cart = document.getElementById("sideCart");
    const overlay = document.getElementById("sideCartOverlay");
    if (cart && overlay) {
        cart.classList.remove("visible");
        overlay.style.display = "none";
        document.body.style.overflow = "";
    }
}

function renderizarSideCart(items, total) {
    const contenedor = document.getElementById("sideCartContent");
    const totalElemento = document.getElementById("sideCartTotal");
    if (!contenedor) return;

    if (!items || items.length === 0) {
        contenedor.innerHTML = "<p class='text-center p-4'>Tu carrito está vacío</p>";
        if (totalElemento) totalElemento.innerText = "$0";
        return;
    }

    let html = "";
    items.forEach(item => {
        html += `
            <div class="cart-item-row">
                <img src="${item.imagen_url}" alt="${item.nombre}">
                <div class="cart-item-details">
                    <h6>${item.nombre}</h6>
                    <p>Talla: ${item.talla} | Color: ${item.color}</p>
                    <div class="d-flex justify-content-between align-items-center mt-1">
                        <span class="text-orange fw-bold">$${item.precio_formateado}</span>
                        <small class="text-muted">Cant: ${item.cantidad}</small>
                    </div>
                </div>
            </div>`;
    });
    contenedor.innerHTML = html;
    if (totalElemento) totalElemento.innerText = `$${total}`;
}

/* =====================================================
    VISTA RÁPIDA (PANEL LATERAL / MODAL)
===================================================== */
function abrirVistaRapida(id) {
    const panel = document.getElementById("vistaRapidaPanel");
    const cont = document.getElementById("contenidoProducto");
    if (!panel || !cont || !id) return;

    panel.classList.replace("hidden", "visible");
    document.body.style.overflow = "hidden";
    cont.innerHTML = `
        <div class="d-flex justify-content-center align-items-center p-5">
            <div class="spinner-border text-primary" role="status"></div>
            <span class="ms-2">Cargando producto...</span>
        </div>`;

    fetch(`/store/vista-rapida/${id}/`)
        .then(res => res.text())
        .then(html => {
            cont.innerHTML = html;
            setTimeout(() => window.initVistaRapida(cont), 50);
        })
        .catch(err => {
            console.error("❌ Error al cargar Vista Rápida:", err);
            cont.innerHTML = "<p class='p-5 text-danger'>Error al cargar el producto.</p>";
        });
}

function cerrarVistaRapida() {
    const panel = document.getElementById("vistaRapidaPanel");
    if (panel) {
        panel.classList.replace("visible", "hidden");
        document.body.style.overflow = "";
    }
}

/* =====================================================
    SINCRONIZACIÓN TIPO TEMU (IMAGEN -> COLOR -> FORM)
===================================================== */
window.initVistaRapida = function(cont) {
    const contenedor = cont || document.getElementById("contenidoProducto");
    if (!contenedor) return;

    const btnAgregar = contenedor.querySelector(".btn-agregar") || document.getElementById("agregarDesdeModal");
    const chipsTallas = contenedor.querySelectorAll(".size-chip");
    const chipsColores = contenedor.querySelectorAll(".color-chip");
    const visor = contenedor.querySelector("#imagen-principal");
    const inputFoto = contenedor.querySelector("#imagen_seleccionada_url");
    const inputColorHidden = contenedor.querySelector("#selected_color_hidden");
    const inputTallaHidden = contenedor.querySelector("#selected_size_hidden");

    let tallaOK = chipsTallas.length === 0 || (inputTallaHidden && inputTallaHidden.value !== "");
    let colorOK = chipsColores.length === 0 || (inputColorHidden && inputColorHidden.value !== "");

    const actualizarEstadoBoton = () => {
        if (!btnAgregar) return;
        if (tallaOK && colorOK) {
            btnAgregar.disabled = false;
            btnAgregar.style.opacity = "1";
            btnAgregar.style.backgroundColor = "#ff6000"; 
            btnAgregar.style.cursor = "pointer";
            btnAgregar.innerHTML = "🛒 Agregar al carrito";
        } else {
            btnAgregar.disabled = true;
            btnAgregar.style.opacity = "0.5";
            btnAgregar.style.cursor = "not-allowed";
            btnAgregar.innerHTML = "Selecciona Talla y Color";
        }
    };

    chipsTallas.forEach(t => {
        t.onclick = function() {
            chipsTallas.forEach(x => x.classList.remove("seleccionado", "btn-dark"));
            this.classList.add("seleccionado", "btn-dark");
            if(inputTallaHidden) inputTallaHidden.value = this.innerText.trim();
            tallaOK = true;
            actualizarEstadoBoton();
        }
    });

    chipsColores.forEach(c => {
        c.onclick = function() {
            chipsColores.forEach(x => x.classList.remove("seleccionado", "btn-dark"));
            this.classList.add("seleccionado", "btn-dark");
            if(inputColorHidden) inputColorHidden.value = this.innerText.trim();
            colorOK = true;
            actualizarEstadoBoton();
        }
    });

    contenedor.querySelectorAll(".miniatura").forEach(miniatura => {
        miniatura.onclick = function() {
            const src = this.dataset.src;
            const colorAsociado = this.dataset.color;
            if(visor) visor.src = src;
            if(inputFoto) inputFoto.value = src;

            contenedor.querySelectorAll(".miniatura").forEach(m => m.classList.remove("activa", "activa-azul"));
            this.classList.add("activa", "activa-azul");

            if (colorAsociado && colorAsociado !== 'base') {
                chipsColores.forEach(chip => {
                    if (chip.innerText.trim().toLowerCase() === colorAsociado.toLowerCase()) {
                        chip.click(); 
                    }
                });
            }
        };
    });
    actualizarEstadoBoton();
};

/* =====================================================
    CONTROLADOR MAESTRO DE AGREGAR AL CARRITO (AJAX)
===================================================== */
document.addEventListener("click", (e) => {
    const btn = e.target.closest("#agregarDesdeModal");
    if (!btn || btn.disabled) return;

    e.preventDefault();
    const form = btn.closest("form");
    if (!form) return;

    const id = btn.dataset.id;
    const formData = new FormData(form);
    const textoOriginal = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Agregando...`;

    fetch(`/store/agregar/${id}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            mostrarToast("¡Producto añadido con éxito! ✅");
            const badge = document.querySelector(".cart-count");
            if (badge) badge.innerText = data.cart_count;

            renderizarSideCart(data.carrito_completo, data.total_carrito);
            cerrarVistaRapida();
            cerrarCarritoModal();
            abrirSideCart();
        } else {
            alert("Error: " + (data.error || "No se pudo agregar"));
        }
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    })
    .catch(err => {
        console.error("❌ Error en Fetch:", err);
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    });
});

/* =====================================================
    UI Y MODALES GLOBALES
===================================================== */
function initEventosGlobales() {
    document.body.addEventListener("click", (e) => {
        const btnQuick = e.target.closest(".quick-view");
        if (btnQuick) { e.preventDefault(); abrirVistaRapida(btnQuick.dataset.id); return; }

        const btnCart = e.target.closest(".jasc-cart");
        if (btnCart) { e.preventDefault(); abrirCarritoModal(btnCart.dataset.id); return; }

        if (e.target.classList.contains("cerrar-panel") || e.target.closest(".cerrar-panel")) cerrarVistaRapida();
        if (e.target.classList.contains("cerrar-carrito") || e.target.closest(".cerrar-carrito")) cerrarCarritoModal();
    });
}

function abrirCarritoModal(id) {
    const modal = document.getElementById("carritoModal");
    const overlay = document.querySelector(".carrito-overlay");
    const cont = document.getElementById("contenidoCarrito");
    if (!modal || !id) return;

    modal.classList.remove("hidden");
    overlay?.classList.remove("hidden");
    document.body.style.overflow = "hidden";
    cont.innerHTML = "<div class='p-4 text-center'><div class='spinner-border'></div></div>";

    fetch(`/store/carrito/${id}/`)
        .then(res => res.text())
        .then(html => { 
            cont.innerHTML = html; 
            setTimeout(() => window.initVistaRapida(cont), 50);
        })
        .catch(() => { cont.innerHTML = "<p class='p-3'>Error al cargar opciones.</p>"; });
}

function cerrarCarritoModal() {
    const modal = document.getElementById("carritoModal");
    const overlay = document.querySelector(".carrito-overlay");
    if (modal) {
        modal.classList.add("hidden");
        overlay?.classList.add("hidden");
        document.body.style.overflow = "";
    }
}

function inicializarCarritoModal() {
    const overlay = document.querySelector(".carrito-overlay");
    overlay?.addEventListener("click", cerrarCarritoModal);
}

/* =====================================================
    EXTRAS: VIDEO HOVER Y SWIPER (FIXED)
===================================================== */
function initSliders() {
    if (typeof Swiper === "undefined") return;
    
    new Swiper(".bannerSwiper", { 
        loop: true, 
        autoplay: { delay: 5000, disableOnInteraction: false }, 
        pagination: { el: ".swiper-pagination", clickable: true } 
    });

    // Slider de Productos Destacados - CORREGIDO
    new Swiper(".destacados-swiper", { 
        slidesPerView: 1.2, 
        spaceBetween: 15,
        grabCursor: true,
        observer: true, 
        observeParents: true,
        watchOverflow: true,
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        breakpoints: { 
            480: { slidesPerView: 2.2 },
            768: { slidesPerView: 3.5 }, 
            1200: { slidesPerView: 5 } 
        } 
    });
}

function initHoverVideoEnGrid() {
    document.querySelectorAll(".product-card .product-image-wrapper").forEach(wrapper => {
        const videoSrc = wrapper.dataset.videoSrc;
        if (!videoSrc) return;
        let videoEl = null;

        wrapper.addEventListener("mouseenter", () => {
            if (videoEl) return;
            videoEl = document.createElement("video");
            videoEl.src = videoSrc;
            videoEl.autoplay = videoEl.muted = videoEl.loop = videoEl.playsInline = true;
            videoEl.className = "product-video";
            videoEl.style.cssText = "width:100%;height:100%;object-fit:cover;position:absolute;top:0;left:0;z-index:1;pointer-events:none;";
            wrapper.appendChild(videoEl);
        });

        wrapper.addEventListener("mouseleave", () => { 
            if (videoEl) { videoEl.remove(); videoEl = null; } 
        });
    });
}