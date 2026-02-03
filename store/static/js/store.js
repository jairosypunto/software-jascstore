/* 🔥 JASCSTORE PRO FULL - MOTOR DE SINCRONIZACIÓN TOTAL */
console.log("🔥 STORE.JS CARGADO - Modo Sincronización Temu PRO Full");

/* =====================================================
    INIT & CONFIGURACIÓN GLOBAL
===================================================== */
document.addEventListener("DOMContentLoaded", () => {
    initEventosGlobales();
    initSliders(); 
    initHoverVideoEnGrid();
    inicializarCarritoModal();
});

function getCSRFToken() { 
    return document.cookie.split(";").find(c => c.trim().startsWith("csrftoken="))?.split("=")[1] || ""; 
}

function mostrarToast(msg) {
    let t = document.getElementById("toast-carrito");
    if (!t) {
        t = document.createElement("div");
        t.id = "toast-carrito";
        document.body.appendChild(t);
    }
    t.className = "toast-carrito visible";
    t.style.backgroundColor = "#0f087e"; 
    t.style.color = "#ffffff";
    t.style.position = "fixed";
    t.style.bottom = "20px";
    t.style.right = "20px";
    t.style.padding = "15px 25px";
    t.style.borderRadius = "8px";
    t.style.zIndex = "9999";
    t.innerText = msg;

    setTimeout(() => { t.className = "toast-carrito"; }, 3000);
}

/* =====================================================
    GESTIÓN DEL SIDE CART (TIPO TEMU)
===================================================== */
function abrirSideCart() {
    const cart = document.getElementById("sideCart");
    const overlay = document.getElementById("sideCartOverlay");
    if (cart && overlay) {
        cart.classList.add("visible");
        overlay.style.display = "block";
        document.body.style.overflow = "hidden";
        obtenerCarritoActualizado(); 
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

    contenedor.innerHTML = "";
    const listaItems = Array.isArray(items) ? items : Object.values(items || {});

    if (listaItems.length === 0) {
        contenedor.innerHTML = `
            <div class="text-center py-5">
                <p class='fw-bold' style='color: #1a237e;'>Tu carrito está vacío</p>
            </div>`;
        if (totalElemento) totalElemento.innerText = "$0";
        return;
    }

    let html = "";
    listaItems.forEach(item => {
        const nombre = item.nombre || "Producto";
        const imagen = item.imagen_url || item.imagen || "/static/img/no-image.png";
        const precio = item.precio_formateado || item.precio || "0";
        const key = item.key || item.item_key;

        const variantInfo = (item.talla || item.color) 
            ? `<p class="mb-1 small text-muted">${item.talla ? 'Talla: '+item.talla : ''} ${item.color ? '| Color: '+item.color : ''}</p>`
            : '';

        html += `
            <div class="cart-item-row d-flex align-items-center mb-3 border-bottom pb-2">
                <img src="${imagen}" alt="${nombre}" style="width:60px; height:60px; object-fit:cover;" class="rounded">
                <div class="cart-item-details flex-grow-1 ms-3">
                    <h6 class="mb-0 fw-bold" style="font-size: 0.9rem; color: #1a237e;">${nombre}</h6>
                    ${variantInfo}
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold" style="color: #1a237e;">$${precio}</span>
                        <div class="d-flex align-items-center gap-2">
                            <small class="text-muted">x${item.cantidad}</small>
                            <button onclick="eliminarItemCarrito('${key}')" class="btn btn-sm text-danger p-1" title="Quitar">
                                <i class="bi bi-trash3"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>`;
    });

    contenedor.innerHTML = html;
    if (totalElemento) {
        totalElemento.innerText = `$${total}`;
        totalElemento.style.color = "#1a237e";
    }
}

function eliminarItemCarrito(itemKey) {
    if(!confirm("¿Deseas eliminar este producto?")) return;
    const encodedKey = encodeURIComponent(itemKey);

    fetch(`/store/carrito/eliminar/${encodedKey}/`, {
        method: "GET",
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            mostrarToast("Producto eliminado 🗑️");
            const badge = document.querySelector(".cart-count");
            if (badge) badge.innerText = data.cart_count;
            if (typeof abrirSideCart === "function") {
                abrirSideCart(); 
            } else {
                renderizarSideCart(data.carrito_completo || data.items || {}, data.total_carrito);
            }
            if(window.location.pathname.includes('carrito')) location.reload();
        }
    })
    .catch(err => console.error("Error:", err));
}

/* =====================================================
    VISTA CARRITO Y VISTA RÁPIDA
===================================================== */
function abrirCarritoModal(id) {
    const modal = document.getElementById("carritoModal");
    const overlay = document.querySelector(".carrito-overlay");
    const cont = document.getElementById("contenidoCarrito");
    
    if (!modal || !id) return;

    // 1. Limpieza de conflictos con Vista Rápida
    const panelVR = document.getElementById("vistaRapidaPanel");
    if (panelVR) {
        panelVR.classList.remove("visible");
        panelVR.style.display = "none";
    }

    modal.classList.remove("hidden");
    modal.style.display = "block";
    
    if (overlay) {
        overlay.style.display = "block";
        overlay.classList.add("overlay-active");
    }

    // Spinner con tu Azul Hermoso [cite: 2026-01-26]
    cont.innerHTML = `<div class='p-5 text-center'><div class='spinner-border' style='color: #0f087e;'></div></div>`;

    fetch(`/store/carrito-modal/${id}/`)
        .then(res => res.text())
        .then(html => { 
            cont.innerHTML = html; 
            
            // Usamos un pequeño delay para asegurar que el DOM cargó
            setTimeout(() => {
                const normalizar = (t) => t ? t.toString().trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") : "";
                
                // --- DETECTAR SI TIENE VARIANTES ---
                const chipsColor = cont.querySelectorAll('.color-chip');
                const chipsTalla = cont.querySelectorAll('.size-chip');
                const hayVariantes = chipsColor.length > 0 || chipsTalla.length > 0;

                const btnFinal = cont.querySelector('#btnAgregarModal') || cont.querySelector('#btnAgregarModalPropio');

                if (!hayVariantes) {
                    // CASO: Producto sin talla ni color (Comedero, Ejercicio)
                    if (btnFinal) {
                        btnFinal.disabled = false;
                        btnFinal.style.backgroundColor = "#0f087e"; // [cite: 2026-01-26]
                        btnFinal.style.opacity = "1";
                        btnFinal.innerHTML = "🛒 AGREGAR AL CARRITO";
                    }
                } else {
                    // CASO: Producto con variantes - Intentar auto-seleccionar por imagen
                    const imgPrincipal = cont.querySelector('#imagen-principal-modal');
                    if (imgPrincipal && chipsColor.length > 0) {
                        const srcActual = imgPrincipal.getAttribute('src');
                        const miniCorrespondiente = cont.querySelector(`.miniatura[data-src="${srcActual}"]`);
                        
                        if (miniCorrespondiente && miniCorrespondiente.dataset.color) {
                            const colorBusca = normalizar(miniCorrespondiente.dataset.color);
                            const btnColor = Array.from(chipsColor).find(b => normalizar(b.dataset.value) === colorBusca);
                            
                            if (btnColor) {
                                btnColor.click(); // Esto disparará tu validador universal
                            }
                        }
                    }
                }

                // Inicializar eventos adicionales si existen
                if (typeof window.initVistaRapida === "function") {
                    window.initVistaRapida(cont); 
                }
            }, 50);
        })
        .catch(err => {
            console.error("Error cargando modal:", err);
            cont.innerHTML = "<p class='p-5 text-center'>Error al cargar el producto.</p>";
        });
}


function abrirVistaRapida(id) {
    const panel = document.getElementById("vistaRapidaPanel");
    const overlayVR = document.getElementById("carritoOverlay");
    const cont = document.getElementById("contenidoProducto");
    
    if (!panel || !cont || !id) return;

    // 1. Limpieza de modales previos
    const modalCarrito = document.getElementById("carritoModal");
    if (modalCarrito) {
        modalCarrito.classList.add("hidden");
        modalCarrito.style.display = "none";
    }

    // 2. Mostrar estructura del modal
    panel.style.display = "block"; 
    panel.classList.remove("hidden");
    panel.classList.add("visible");

    if (overlayVR) {
        overlayVR.style.display = "block";
        overlayVR.classList.add("visible");
        overlayVR.style.opacity = "1";
    }

    document.body.style.overflow = "hidden";
    
    // Spinner con tu Azul Hermoso
    cont.innerHTML = `<div class="d-flex justify-content-center p-5"><div class="spinner-border" style="color: #0f087e;"></div></div>`;

    // 3. Petición al servidor (Ruta absoluta para Home/Store)
    fetch(`/store/vista-rapida/${id}/`)
        .then(res => res.text())
        .then(html => {
            cont.innerHTML = html;
            
            setTimeout(() => {
                const imgPrincipal = document.getElementById('imagen-principal-modal');
                const botonesColor = cont.querySelectorAll('.color-chip');
                const miniaturas = cont.querySelectorAll('.miniatura');

                // --- LÓGICA DE SINCRONIZACIÓN MAESTRA ---
                botonesColor.forEach(boton => {
                    boton.addEventListener('click', function(e) {
                        e.preventDefault();
                        
                        // A. Activar visualmente el botón (Azul Hermoso)
                        botonesColor.forEach(b => b.classList.remove('seleccionado', 'active'));
                        this.classList.add('seleccionado', 'active');

                        // Normalizamos el valor para evitar errores de comparación
                        const colorBuscado = this.getAttribute('data-value').trim().toLowerCase();

                        // B. Sincronizar Miniaturas (Vital para que el Carrito NO falle)
                        miniaturas.forEach(m => {
                            m.classList.remove('active', 'selected');
                        });

                        // Buscamos la miniatura comparando en minúsculas para mayor seguridad
                        const miniCorrespondiente = Array.from(miniaturas).find(m => {
                            const mColor = m.getAttribute('data-color');
                            return mColor && mColor.trim().toLowerCase() === colorBuscado;
                        });
                        
                        if (miniCorrespondiente) {
                            // Marcamos como activa para que el script del carrito capture ESTA imagen
                            miniCorrespondiente.classList.add('active', 'selected');
                            
                            // C. Cambiar Imagen Principal
if (imgPrincipal) {
    const nuevaRuta = miniCorrespondiente.getAttribute('data-src');
    imgPrincipal.src = nuevaRuta;
    
    // Sincronizar el input oculto para que el envío AJAX lo vea
    const inputImagenOculto = cont.querySelector('#imagen_seleccionada_url');
    if (inputImagenOculto) {
        inputImagenOculto.value = nuevaRuta;
    }
}
                        }

                        // D. Actualizar el Input Oculto del Formulario (Para Checkout y Factura)
                        const inputColor = cont.querySelector('input[name="color"]');
                        if (inputColor) {
                            inputColor.value = this.getAttribute('data-value'); // Valor original
                        }

                        console.log("JascStore: Sistema sincronizado para el color:", colorBuscado);
                    });
                });

                // --- Inicialización: Simular clic en el primer color disponible ---
                if (botonesColor.length > 0) {
                    // Si ya hay uno con clase 'seleccionado' de servidor, usamos ese, si no el primero
                    const btnInicial = cont.querySelector('.color-chip.seleccionado') || botonesColor[0];
                    btnInicial.click(); 
                }

                // Ejecutar lógica interna (tallas, validaciones de stock)
                if (typeof window.initVistaRapida === "function") {
                    window.initVistaRapida(cont);
                }
            }, 250);
        })
        .catch(err => {
            console.error("Error crítico en JascStore:", err);
            cont.innerHTML = "<p class='text-center p-4'>Error al conectar con el servidor.</p>";
        });
}


function cerrarVistaRapida() {
    const panel = document.getElementById("vistaRapidaPanel");
    const cont = document.getElementById("contenidoProducto");
    if (panel) {
        panel.classList.replace("visible", "hidden");
        panel.scrollTop = 0;
        document.body.style.overflow = "auto";
        document.documentElement.style.overflow = "auto"; 
        if (cont) cont.innerHTML = "";
    }
}

/* =====================================================
    SINCRONIZACIÓN MAESTRA (IMAGEN -> COLOR -> FORM)
===================================================== */
window.initVistaRapida = function(cont) {
    const contenedor = cont || document.getElementById("contenidoProducto");
    if (!contenedor) return;

    const btnAgregar = contenedor.querySelector(".btn-agregar, #btnAgregarModal, #btnAgregarFinal");
    const chipsTallas = contenedor.querySelectorAll(".size-chip");
    const chipsColores = contenedor.querySelectorAll(".color-chip");
    const visor = contenedor.querySelector("#imagen-principal, #imagen-principal-modal, .imagen-principal img");
    const inputFoto = contenedor.querySelector("#imagen_seleccionada_url");
    const inputColorHidden = contenedor.querySelector("#selected_color_hidden, input[name='color']");
    const inputTallaHidden = contenedor.querySelector("#selected_size_hidden, input[name='talla']");

    if (visor && inputFoto && visor.src) inputFoto.value = visor.src;

    let tallaOK = chipsTallas.length === 0 || (inputTallaHidden && inputTallaHidden.value !== "");
    let colorOK = chipsColores.length === 0 || (inputColorHidden && inputColorHidden.value !== "");

    const actualizarEstadoBoton = () => {
        if (!btnAgregar) return;
        if (tallaOK && colorOK) {
            btnAgregar.disabled = false;
            btnAgregar.style.backgroundColor = "#0f087e";
            btnAgregar.style.opacity = "1";
            btnAgregar.innerHTML = "🛒 Agregar al carrito";
        } else {
            btnAgregar.disabled = true;
            btnAgregar.style.backgroundColor = "#6c757d";
            btnAgregar.style.opacity = "0.5";
            btnAgregar.innerHTML = "Selecciona Talla y Color";
        }
    };

    chipsTallas.forEach(t => {
        t.onclick = function(e) {
            e.preventDefault();
            chipsTallas.forEach(x => { x.classList.remove("seleccionado"); x.style.backgroundColor = ""; });
            this.classList.add("seleccionado");
            this.style.backgroundColor = "#0f087e";
            this.style.color = "white";
            if(inputTallaHidden) inputTallaHidden.value = this.dataset.value || this.innerText.trim();
            tallaOK = true;
            actualizarEstadoBoton();
        }
    });

    chipsColores.forEach(c => {
        c.onclick = function(e) {
            e.preventDefault();
            chipsColores.forEach(x => { x.classList.remove("seleccionado"); x.style.backgroundColor = ""; });
            this.classList.add("seleccionado");
            this.style.backgroundColor = "#0f087e";
            this.style.color = "white";
            if(inputColorHidden) inputColorHidden.value = this.dataset.value || this.innerText.trim();
            colorOK = true;
            actualizarEstadoBoton();
        }
    });

    const miniaturas = contenedor.querySelectorAll(".miniatura");
    miniaturas.forEach(miniatura => {
        miniatura.onclick = function() {
            const src = this.dataset.src || this.querySelector('img')?.src;
            const colorAsociado = this.dataset.color || this.dataset.value;
            if(visor) visor.src = src;
            if(inputFoto) inputFoto.value = src;

            miniaturas.forEach(m => { m.style.borderColor = "#ddd"; m.classList.remove("activa-azul"); });
            this.classList.add("activa-azul");
            this.style.borderColor = "#0f087e";

            if (colorAsociado && colorAsociado !== 'base') {
                chipsColores.forEach(chip => {
                    const textoChip = (chip.getAttribute("data-value") || chip.innerText.trim()).toLowerCase();
                    if (textoChip === colorAsociado.toLowerCase()) {
                        if(!chip.classList.contains("seleccionado")) chip.click(); 
                    }
                });
            }
        };
    });
    actualizarEstadoBoton();
};

/* =====================================================
    CONTROLADOR AJAX AGREGAR Y UI FINAL
===================================================== */
document.addEventListener("click", (e) => {
    const isCheckout = e.target.closest(".btn-pagar, #btn-finalizar-checkout") || (e.target.tagName === 'A' && e.target.href.includes('checkout'));
    if (isCheckout) return; 

    const btn = e.target.closest(".jasc-cart, #btnAgregarModal, #btnConfirmarCarrito, .btn-agregar");
    if (!btn) return;

    const tieneVariantes = btn.getAttribute("data-has-variants") === "true";
    const esBotonDeTarjeta = !btn.closest("form");

    if (esBotonDeTarjeta && tieneVariantes) {
        e.preventDefault();
        abrirCarritoModal(btn.dataset.id);
        return;
    }

    if (btn.disabled) return;
    e.preventDefault();
    const form = btn.closest("form");
    if (!form) return;

const productId = btn.dataset.id || btn.dataset.productId;
const formData = new FormData(form);

// 🔥 PARCHE JASCSTORE: Capturar la imagen seleccionada del modal
const inputImagen = form.querySelector("#imagen_seleccionada_url");
if (inputImagen && inputImagen.value) {
    formData.set('imagen_seleccionada_url', inputImagen.value);
}

const textoOriginal = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;

    fetch(`/store/agregar/${productId}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            mostrarToast("¡Añadido! ✅");
            document.querySelectorAll(".cart-count").forEach(b => b.innerText = data.cart_count);
            renderizarSideCart(data.carrito_completo, data.total_carrito);
            cerrarVistaRapida();
            cerrarCarritoModal();
            abrirSideCart();
        }
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    });
});

function cerrarCarritoModal() {
    const modal = document.getElementById("carritoModal");
    const overlay = document.querySelector(".carrito-overlay");
    if (modal) { modal.classList.add("hidden"); modal.style.display = "none"; }
    if (overlay) { overlay.classList.add("hidden"); overlay.style.display = "none"; }
    document.body.style.overflow = "auto";
    document.documentElement.style.overflow = "auto";
    const contCarrito = document.getElementById("contenidoCarrito");
    if (contCarrito) contCarrito.innerHTML = ""; 
}

function inicializarCarritoModal() {
    document.querySelector(".carrito-overlay")?.addEventListener("click", cerrarCarritoModal);
}

function initSliders() {
    if (typeof Swiper === "undefined") return;
    new Swiper(".bannerSwiper", { loop: true, autoplay: { delay: 5000 }, pagination: { el: ".swiper-pagination", clickable: true } });
    new Swiper(".destacados-swiper", { 
        slidesPerView: 1.2, spaceBetween: 15, autoplay: { delay: 3000 },
        navigation: { nextEl: ".swiper-button-next", prevEl: ".swiper-button-prev" },
        breakpoints: { 480: { slidesPerView: 2.2 }, 768: { slidesPerView: 3.5 }, 1200: { slidesPerView: 5 } } 
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
            videoEl.src = videoSrc; videoEl.autoplay = videoEl.muted = videoEl.loop = videoEl.playsInline = true;
            videoEl.style.cssText = "width:100%;height:100%;object-fit:cover;position:absolute;top:0;left:0;z-index:1;pointer-events:none;";
            wrapper.appendChild(videoEl);
        });
        wrapper.addEventListener("mouseleave", () => { if (videoEl) { videoEl.remove(); videoEl = null; } });
    });
}

function obtenerCarritoActualizado() {
    fetch('/store/carrito-json/', { headers: { "X-Requested-With": "XMLHttpRequest" }})
    .then(res => res.json())
    .then(data => data.carrito_completo && renderizarSideCart(data.carrito_completo, data.total_carrito))
    .catch(err => console.error("Error:", err));
}

function initEventosGlobales() {
    document.body.addEventListener("click", (e) => {
        const btnQuick = e.target.closest(".quick-view");
        if (btnQuick) { e.preventDefault(); abrirVistaRapida(btnQuick.dataset.id); }
    });
}



