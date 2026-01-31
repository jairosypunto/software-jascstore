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
        // --- AGREGAR ESTA LÍNEA PARA ACTUALIZAR AL ABRIR ---
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

    // 1. Limpieza inicial
    contenedor.innerHTML = "";

    // 2. Convertimos a Array de forma segura (Asegura que no se borre todo si los datos vienen distintos)
    const listaItems = Array.isArray(items) ? items : Object.values(items || {});

    // 3. Si no hay nada, mostrar mensaje en Azul Hermoso
    if (listaItems.length === 0) {
        contenedor.innerHTML = `
            <div class="text-center py-5">
                <p class='fw-bold' style='color: #1a237e;'>Tu carrito está vacío</p>
            </div>`;
        if (totalElemento) totalElemento.innerText = "$0";
        return;
    }

    // 4. Construcción del HTML asegurando que cada producto se dibuje
    let html = "";
    listaItems.forEach(item => {
        // Validación de datos para evitar que el script se rompa
        const nombre = item.nombre || "Producto";
        const imagen = item.imagen_url || item.imagen || "/static/img/no-image.png";
        const precio = item.precio_formateado || item.precio || "0";
        const key = item.key || item.item_key; // La llave para poder borrar individualmente

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

    // 5. Inyectamos todo el HTML de una sola vez para que sea rápido
    contenedor.innerHTML = html;

    // 6. Actualizamos el Subtotal sin neón
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
            
            // 1. Actualizamos el contador del navbar
            const badge = document.querySelector(".cart-count");
            if (badge) badge.innerText = data.cart_count;

            // 2. LA SOLUCIÓN: En lugar de intentar dibujar nosotros, 
            // llamamos a la función que ya sabemos que funciona al abrir el carrito.
            if (typeof abrirSideCart === "function") {
                abrirSideCart(); 
            } else {
                // Si no existe esa función, recargamos la data directamente
                renderizarSideCart(data.carrito_completo || data.items || {}, data.total_carrito);
            }

            // 3. Si estás en la página principal de carrito, recarga la web
            if(window.location.pathname.includes('carrito')) location.reload();
        }
    })
    .catch(err => console.error("Error:", err));
}

/* =====================================================
    VISTA CARRITO (MODAL LATERAL)
===================================================== */
function abrirCarritoModal(id) {
    const modal = document.getElementById("carritoModal");
    const overlay = document.querySelector(".carrito-overlay");
    const cont = document.getElementById("contenidoCarrito");
    
    if (!modal || !id) return;

    // --- CORRECCIÓN DE OPACIDAD ---
    // Cerramos la vista rápida antes para evitar doble fondo oscuro
    const panelVR = document.getElementById("vistaRapidaPanel");
    if (panelVR) panelVR.classList.remove("visible");

    modal.classList.remove("hidden");
    modal.style.display = "block";
    
    // Activamos el overlay correctamente
    if (overlay) {
        overlay.style.display = "block";
        overlay.classList.add("overlay-active"); // Clase para controlar opacidad
    }

    cont.innerHTML = `
        <div class='p-5 text-center'>
            <div class='spinner-border' style='color: #1a237e; width: 3rem; height: 3rem;'></div>
            <p class='mt-3 fw-bold' style='color: #1a237e;'>Cargando opciones...</p>
        </div>`;

    fetch(`/store/carrito-modal/${id}/`)
        .then(res => {
            if (!res.ok) throw new Error("404/500 Server Error");
            return res.text();
        })
        .then(html => { 
            if (cont) {
                cont.innerHTML = html; 
                setTimeout(() => {
                    if (typeof window.initVistaRapida === "function") {
                        window.initVistaRapida(cont); 
                    }
                }, 50);
            }
        })
        .catch(err => { 
            console.error("🔴 Error:", err);
            cont.innerHTML = "<p class='p-4 text-center text-danger'>Error al cargar opciones.</p>"; 
        });
}

/* =====================================================
    VISTA RÁPIDA (MODAL CENTRAL) - JascStore PRO Full
===================================================== */
function abrirVistaRapida(id) {
    const panel = document.getElementById("vistaRapidaPanel");
    const overlayVR = document.getElementById("carritoOverlay");
    const cont = document.getElementById("contenidoProducto");
    
    if (!panel || !cont || !id) return;

    // 1. Limpiar estados previos
    const modalCarrito = document.getElementById("carritoModal");
    if (modalCarrito) {
        modalCarrito.classList.add("hidden");
        modalCarrito.style.display = "none";
    }

    panel.style.display = "block"; 
    panel.classList.remove("hidden");
    panel.classList.add("visible");

    if (overlayVR) {
        overlayVR.style.display = "block";
        overlayVR.classList.add("visible");
        overlayVR.style.opacity = "1";
    }

    cont.innerHTML = "";
    document.body.style.overflow = "hidden";

    // 2. Loader con tu Azul Hermoso
    cont.innerHTML = `
        <div class="d-flex justify-content-center align-items-center p-5" style="min-height: 450px;">
            <div class="spinner-border" style="color: #1a237e; width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>`;

    // 3. Carga de datos
    fetch(`/store/vista-rapida/${id}/`)
        .then(res => {
            if (!res.ok) throw new Error("Producto no encontrado");
            return res.text();
        })
        .then(html => {
            cont.innerHTML = html;
            
            // --- INICIO MODO SINCRONIZACIÓN PRO ---
            // Usamos un pequeño delay para asegurar que el DOM esté listo
            setTimeout(() => {
                const botones = cont.querySelectorAll('.option-chip');
                
                botones.forEach(btn => {
                    // Lógica de Bloqueo (La que probaste en F12)
                    if (btn.classList.contains('agotado') || btn.classList.contains('disabled') || btn.innerText.trim() === "") {
                        btn.disabled = true;
                        btn.classList.add('btn-disabled');
                        btn.style.opacity = "0.3";
                        btn.style.pointerEvents = "none";
                        btn.style.textDecoration = "line-through"; // Tachado visual extra
                    }

                    // Lógica de Selección Azul Hermoso
                    btn.addEventListener('click', function() {
                        if (this.disabled) return;
                        
                        // Limpiar grupo
                        const parent = this.closest('.opciones') || this.parentElement;
                        parent.querySelectorAll('.option-chip').forEach(b => {
                            b.classList.remove('seleccionado', 'btn-dark');
                            b.style.backgroundColor = ""; // Resetear a blanco
                            b.style.color = "";
                        });

                        // Aplicar tu Azul Hermoso
                        this.classList.add('seleccionado', 'btn-dark');
                        this.style.backgroundColor = "#1a237e";
                        this.style.color = "white";
                    });
                });

                console.log("✅ JascStore: Opciones sincronizadas y bloqueadas.");

                if (typeof window.initVistaRapida === "function") {
                    window.initVistaRapida(cont);
                }
            }, 100); 
        })
        .catch(err => {
            console.error("Error:", err);
            cont.innerHTML = `<div class="text-center p-5"><p>Error al cargar el producto.</p></div>`;
        });
}

function cerrarVistaRapida() {
    const panel = document.getElementById("vistaRapidaPanel");
    const overlay = document.getElementById("carritoOverlay");
    if (panel) panel.style.display = "none";
    if (overlay) overlay.style.display = "none";
    document.body.style.overflow = "auto";
}

function cerrarVistaRapida() {
    const panel = document.getElementById("vistaRapidaPanel");
    const overlay = document.getElementById("carritoOverlay");
    
    if (panel) {
        panel.classList.add("hidden");
        panel.classList.remove("visible");
        panel.style.display = "none";
    }
    if (overlay) {
        overlay.style.display = "none";
        overlay.classList.remove("visible");
    }
    document.body.style.overflow = "auto"; // Restaurar scroll
}

function cerrarVistaRapida() {
    const panel = document.getElementById("vistaRapidaPanel");
    const overlay = document.getElementById("carritoOverlay");
    if (panel) panel.style.display = "none";
    if (overlay) overlay.style.display = "none";
    document.body.style.overflow = "auto";
}

/* Función para cerrar que limpie todo */
function cerrarVistaRapida() {
    const panel = document.getElementById("vistaRapidaPanel");
    const overlay = document.getElementById("carritoOverlay");
    
    if (panel) {
        panel.classList.add("hidden");
        panel.classList.remove("visible");
        panel.style.display = "none";
    }
    if (overlay) {
        overlay.style.display = "none";
        overlay.classList.remove("visible");
    }
    document.body.style.overflow = "auto";
}

/* =====================================================
    CERRAR VISTA RÁPIDA (PANEL LATERAL / MODAL)
    Restaura el control del sitio al usuario - JascStore
===================================================== */
function cerrarVistaRapida() {
    const panel = document.getElementById("vistaRapidaPanel");
    const cont = document.getElementById("contenidoProducto");

    if (panel) {
        // 1. Cambiamos el estado visual del panel a oculto
        panel.classList.replace("visible", "hidden");
        
        // 2. REFUERZO DE LIMPIEZA: Resetear el scroll interno del panel
        // Esto evita que el próximo producto aparezca "cortado" o desde abajo
        panel.scrollTop = 0;

        // 3. Devolvemos el scroll al cuerpo de la página (Home o Tienda)
        // Usamos "auto" para asegurar que el navegador recalcule el scrollbar
        document.body.style.overflow = "auto";
        document.documentElement.style.overflow = "auto"; 

        // 4. Limpiamos el contenido para que la siguiente apertura sea limpia
        if (cont) {
            cont.innerHTML = "";
        }
    }
}

/* =====================================================
   SINCRONIZACIÓN TIPO TEMU (IMAGEN -> COLOR -> FORM)
===================================================== */
window.initVistaRapida = function(cont) {
    const contenedor = cont || document.getElementById("contenidoProducto");
    if (!contenedor) return;

    // 1. Detección de Botones
    const btnAgregar = contenedor.querySelector(".btn-agregar") || 
                       document.getElementById("btnAgregarModal") ||
                       document.getElementById("agregarDesdeModal") || 
                       document.getElementById("btnAgregarFinal");

    const chipsTallas = contenedor.querySelectorAll(".size-chip");
    const chipsColores = contenedor.querySelectorAll(".color-chip");
    const visor = contenedor.querySelector("#imagen-principal") || 
                  contenedor.querySelector("#imagen-principal-modal") ||
                  contenedor.querySelector(".imagen-principal img"); // Tercer intento por si acaso
    
    const inputFoto = contenedor.querySelector("#imagen_seleccionada_url");
    const inputColorHidden = contenedor.querySelector("#selected_color_hidden") || contenedor.querySelector("input[name='color']");
    const inputTallaHidden = contenedor.querySelector("#selected_size_hidden") || contenedor.querySelector("input[name='talla']");

    // Sincronización Inicial: Si el visor ya tiene imagen, la mandamos al input para que no vaya vacío
    if (visor && inputFoto && visor.src) {
        inputFoto.value = visor.src;
    }

    let tallaOK = chipsTallas.length === 0 || (inputTallaHidden && inputTallaHidden.value !== "");
    let colorOK = chipsColores.length === 0 || (inputColorHidden && inputColorHidden.value !== "");

    const actualizarEstadoBoton = () => {
        if (!btnAgregar) return;
        if (tallaOK && colorOK) {
            btnAgregar.disabled = false;
            btnAgregar.style.opacity = "1";
            btnAgregar.style.backgroundColor = "#0f087e"; 
            btnAgregar.style.cursor = "pointer";
            btnAgregar.innerHTML = "🛒 Agregar al carrito";
        } else {
            btnAgregar.disabled = true;
            btnAgregar.style.opacity = "0.5";
            btnAgregar.innerHTML = "Selecciona Talla y Color";
        }
    };

    // --- Tallas ---
    chipsTallas.forEach(t => {
        t.onclick = function() {
            chipsTallas.forEach(x => x.classList.remove("seleccionado", "btn-dark"));
            this.classList.add("seleccionado", "btn-dark");
            const valor = this.getAttribute("data-value") || this.innerText.trim();
            if(inputTallaHidden) inputTallaHidden.value = valor;
            tallaOK = true;
            actualizarEstadoBoton();
        }
    });

    // --- Colores ---
    chipsColores.forEach(c => {
        c.onclick = function() {
            chipsColores.forEach(x => x.classList.remove("seleccionado", "btn-dark"));
            this.classList.add("seleccionado", "btn-dark");
            const valorColor = this.getAttribute("data-value") || this.getAttribute("data-color") || this.innerText.trim();
            if(inputColorHidden) inputColorHidden.value = valorColor;
            colorOK = true;
            actualizarEstadoBoton();
        }
    });

    // --- Miniaturas (Sincronización Reforzada) ---
    const miniaturas = contenedor.querySelectorAll(".miniatura");
    miniaturas.forEach(miniatura => {
        miniatura.onclick = function() {
            // Buscamos la URL: 1. data-src, 2. src de la imagen interna, 3. src del elemento mismo
            const imgInterna = this.querySelector('img');
            const src = this.dataset.src || (imgInterna ? imgInterna.src : this.src);
            const colorAsociado = this.dataset.color || this.dataset.value;
            
            if(visor) {
                visor.src = src;
                console.log("✅ Visor actualizado:", src);
            }
            
            if(inputFoto) {
                inputFoto.value = src; // SE ENVÍA ESTA URL AL SERVIDOR
                console.log("✅ Input de imagen actualizado:", src);
            }

            // Estilo visual de miniatura activa
            miniaturas.forEach(m => m.classList.remove("activa", "activa-azul", "border-primary"));
            this.classList.add("activa", "activa-azul", "border-primary");

            // Sincronización Automática con Colores
            if (colorAsociado && colorAsociado !== 'base') {
                chipsColores.forEach(chip => {
                    const textoChip = (chip.getAttribute("data-value") || chip.innerText.trim()).toLowerCase();
                    if (textoChip === colorAsociado.toLowerCase()) {
                        // Solo hacemos clic si no está seleccionado para evitar bucles
                        if(!chip.classList.contains("seleccionado")) chip.click(); 
                    }
                });
            }
        };
    });

    actualizarEstadoBoton();
};


/* =====================================================
    CONTROLADOR MAESTRO DE AGREGAR AL CARRITO (AJAX)
    Estado: Blindaje Total - Integración JascStore
===================================================== */
document.addEventListener("click", (e) => {
    // 1. VALIDACIÓN DE CHECKOUT (PRIORIDAD 0)
    const isCheckout = e.target.closest(".btn-pagar") || 
                       e.target.closest("#btn-finalizar-checkout") || 
                       (e.target.tagName === 'A' && e.target.href.includes('checkout'));

    if (isCheckout) return; 

    // 2. BUSCAR BOTÓN DE AGREGAR O APERTURA DE MODAL
    // Capturamos el botón azul de la tarjeta (.jasc-cart) y los botones internos de los modales
    const btn = e.target.closest(".jasc-cart") || 
                e.target.closest("#btnAgregarModal") || 
                e.target.closest("#btnConfirmarCarrito") || 
                e.target.closest(".btn-agregar");

    if (!btn) return;

    // 🟢 LÓGICA DE APERTURA: Si el botón es de la tarjeta y tiene variantes
    const tieneVariantes = btn.getAttribute("data-has-variants") === "true";
    const esBotonDeTarjeta = !btn.closest("form"); // Si no está dentro de un form, es el de la tarjeta

    if (esBotonDeTarjeta && tieneVariantes) {
        e.preventDefault();
        const productId = btn.dataset.id;
        console.log("📦 Detectadas variantes. Abriendo selección para ID:", productId);
        
        // Llamamos a la función que carga el modal de vista_carrito.html
        if (typeof abrirCarritoModal === "function") {
            abrirCarritoModal(productId);
        } else {
            console.error("❌ Error: La función abrirCarritoModal no está definida.");
        }
        return; // IMPORTANTE: Detenemos aquí para que NO intente hacer el AJAX sin datos
    }

    // 3. PROCESO AJAX (Solo cuando ya estamos dentro del modal y los datos están listos)
    if (btn.disabled) return;
    
    e.preventDefault();
    
    const form = btn.closest("form");
    if (!form) return;

    const productId = btn.dataset.id || btn.dataset.productId;
    const formData = new FormData(form);
    const textoOriginal = btn.innerHTML;

    // Feedback visual en tu Azul Hermoso
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;

    fetch(`/store/agregar/${productId}/`, {
        method: "POST",
        headers: { 
            "X-CSRFToken": getCSRFToken(), 
            "X-Requested-With": "XMLHttpRequest" 
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            mostrarToast("¡Añadido! ✅");
            document.querySelectorAll(".cart-count").forEach(b => b.innerText = data.cart_count);
            
            if (typeof renderizarSideCart === "function") {
                renderizarSideCart(data.carrito_completo, data.total_carrito);
            }
            
            // Cerramos lo que sea que esté abierto
            if (typeof cerrarVistaRapida === "function") cerrarVistaRapida();
            if (typeof cerrarCarritoModal === "function") cerrarCarritoModal();
            if (typeof abrirSideCart === "function") abrirSideCart();
        }
    })
    .catch(err => console.error("Error AJAX:", err))
    .finally(() => {
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



// 4. Función de cierre obligatoria - Actualizada JascStore
function cerrarCarritoModal() {
    const modal = document.getElementById("carritoModal");
    const overlay = document.querySelector(".carrito-overlay");
    const sideOverlay = document.querySelector(".side-cart-overlay"); // Capa extra detectada en inspector

    // 1. Ocultamos el modal principal
    if (modal) {
        modal.classList.add("hidden");
        modal.style.display = "none";
    }

    // 2. Ocultamos TODAS las capas oscuras (overlays)
    // Esto es vital para que el "ojo" pueda recibir el clic
    if (overlay) {
        overlay.classList.add("hidden");
        overlay.style.display = "none";
    }
    
    if (sideOverlay) {
        sideOverlay.style.display = "none";
    }

    // 3. RESTAURACIÓN CRÍTICA DEL SCROLL
    // Si no haces esto, al abrir el ojo la pantalla estará bloqueada o desplazada
    document.body.style.overflow = "auto";
    document.body.style.paddingRight = "0px"; // Quita el salto que a veces deja el scroll de Bootstrap
    document.documentElement.style.overflow = "auto";

    // 4. Limpieza de rastro visual (Evita el espacio en blanco del pantallazo 3)
    const contCarrito = document.getElementById("contenidoCarrito");
    if (contCarrito) {
        contCarrito.innerHTML = ""; 
    }
}

function inicializarCarritoModal() {
    const overlay = document.querySelector(".carrito-overlay");
    overlay?.addEventListener("click", cerrarCarritoModal);
}

/* =====================================================
    EXTRAS: VIDEO HOVER Y SWIPER
===================================================== */
function initSliders() {
    if (typeof Swiper === "undefined") return;
    
    new Swiper(".bannerSwiper", { 
        loop: true, 
        autoplay: { delay: 5000 }, 
        pagination: { el: ".swiper-pagination", clickable: true } 
    });

    const destacadosSwiper = new Swiper(".destacados-swiper", { 
        slidesPerView: 1.2, 
        spaceBetween: 15,
        autoplay: { delay: 3000 },
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

/* Refresca los datos del Side Cart sin recargar la página */
// store.js
function obtenerCarritoActualizado() {
    fetch('/store/carrito-json/', { 
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => {
        // Verificamos si la respuesta es realmente JSON antes de procesar
        const contentType = res.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return res.json();
        } else {
            throw new Error("El servidor no devolvió JSON. Revisa tus URLs.");
        }
    })
    .then(data => {
        if (data.carrito_completo) {
            renderizarSideCart(data.carrito_completo, data.total_carrito);
        }
    })
    .catch(err => console.error("Error al refrescar el carrito:", err));
}

// Función para limpiar TODO antes de abrir un nuevo modal
function limpiarModales() {
    // Forzar que el scroll del cuerpo regrese si quedó bloqueado
    document.body.style.overflow = 'auto';
    
    // Si usas overlays oscuros manuales, ocúltalos todos
    const overlays = document.querySelectorAll('.vista-rapida-overlay, .side-cart-overlay');
    overlays.forEach(el => el.style.display = 'none');

    // Limpiar el contenido interno para que no se vea lo anterior (Pantallazo 3)
    const contenido = document.getElementById('contenidoProducto');
    if(contenido) contenido.innerHTML = ''; 
}

// Llama a limpiarModales() justo antes de ejecutar la lógica de abrir el "Ojo"
document.querySelectorAll('.jasc-quick-view').forEach(btn => {
    btn.addEventListener('click', () => {
        limpiarModales();
        // ... aquí sigue tu código para abrir la vista rápida ...
    });
});

