# ============================
# Librerías estándar de Python
# ============================
from decimal import Decimal
from io import BytesIO

# ============================
# Librerías Django
# ============================
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import localtime
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage

# ============================
# Modelos propios
# ============================
from .models import Product, Factura, DetalleFactura, Banner, Category, ProductVariant
from .forms import CheckoutForm

# ============================
# Utilidades propias
# ============================
from store.utils import formatear_numero
from store.utils.totales import calcular_totales
from store.utils.email import enviar_factura   # ✅ Función de correo con SendGrid

# ============================
# Librerías externas (ReportLab para PDF)
# ============================
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# ============================================================
# 🧮 Función auxiliar: cálculo de precio final con descuento
# ============================================================
def _precio_final(producto: Product) -> Decimal:
    """
    Devuelve el precio final del producto aplicando descuento.
    Usa la propiedad del modelo si existe; si no, lo calcula aquí.
    """
    try:
        return producto.final_price  # ✅ propiedad definida en Product
    except AttributeError:
        discount = getattr(producto, 'discount', 0) or 0
        cost = Decimal(str(producto.cost))
        if discount > 0:
            return cost * (Decimal('1') - Decimal(discount) / Decimal('100'))
        return cost

# ============================================================
# 🛒 Función auxiliar: construir lista de ítems del carrito
# ============================================================
def _items_carrito(request):
    """Construye la lista de ítems sincronizando imagen, stock real y variantes."""
    carrito = request.session.get('carrito', {})
    items = []
    
    # Obtenemos los productos de la DB de forma eficiente
    ids = [item['producto_id'] for item in carrito.values()]
    productos_db = Product.objects.in_bulk(ids)

    for key, item in carrito.items():
        producto = productos_db.get(item['producto_id'])
        if not producto:
            continue

        precio_unitario = Decimal(str(item.get('precio', 0)))
        cantidad = int(item.get('cantidad', 0))
        talla = item.get('talla', '')
        color = item.get('color', '')
        
        # 1. CORRECCIÓN DE IMAGEN: 
        # Buscamos 'imagen_url' (que es como lo guarda tu views.py)
        imagen_final = item.get('imagen_url') or item.get('imagen') or (producto.image.url if producto.image else "")

        # 2. VALIDACIÓN DE STOCK REAL (Variante):
        # Buscamos la variante en la tabla de stock para habilitar botones y quitar el "Agotado"
        variante = ProductVariant.objects.filter(
            product=producto, 
            talla=talla, 
            color=color
        ).first()
        
        stock_max = variante.stock if variante else 0

        items.append({
            'producto_id': item['producto_id'],
            'item_key': key,
            'nombre': item.get('nombre', producto.name),
            'talla': talla,
            'color': color,
            'cantidad': cantidad,
            'precio': precio_unitario,
            'subtotal': precio_unitario * cantidad, # Usamos 'subtotal' para tu carrito.html
            'imagen_url': imagen_final,             # Cambiado a 'imagen_url' para tu carrito.html
            'stock_max': stock_max,                 # Para habilitar el botón "+"
            'disponible': stock_max > 0,            # Para quitar el mensaje "Agotado"
            'producto': producto,
        })
    return items

# ============================================================
# 📋 Vista: Ver carrito (ACTUALIZADA Y BLINDADA)
# ============================================================
from django.shortcuts import render
from django.contrib import messages
from decimal import Decimal
from store.models import Product, ProductVariant 

def ver_carrito(request):
    carrito = request.session.get("carrito", {})
    total = Decimal("0")
    productos_carrito = []
    carrito_valido = True 

    if not carrito:
        carrito_valido = False

    for key, item in carrito.items():
        p_id = item.get("producto_id")
        talla_val = str(item.get("talla", "")).strip()
        color_val = str(item.get("color", "")).strip()

        # 1. Intento de búsqueda precisa (Producto + Talla + Color)
        variante = ProductVariant.objects.filter(
            product_id=p_id, 
            talla__iexact=talla_val, 
            color__iexact=color_val
        ).first()

        # 2. Si falla (por ser Color Único o estar vacío), buscamos solo por Talla
        if not variante:
            variante = ProductVariant.objects.filter(
                product_id=p_id, 
                talla__iexact=talla_val
            ).first()

        # Validación de stock
        if not variante or variante.stock <= 0:
            disponible = False
            carrito_valido = False
            stock_actual = 0
        else:
            disponible = True
            stock_actual = variante.stock
            if item["cantidad"] > stock_actual:
                item["cantidad"] = stock_actual
                request.session.modified = True

        precio = Decimal(str(item.get("precio", 0)))
        subtotal = precio * item["cantidad"]
        total += subtotal

        productos_carrito.append({
            "item_key": key,
            "nombre": item.get("nombre"),
            "precio": precio,
            "cantidad": item["cantidad"],
            "talla": talla_val,
            "color": color_val,
            "imagen_url": item.get("imagen_url"),
            "subtotal": subtotal,
            "disponible": disponible,
            "stock_max": stock_actual
        })

    context = {
        "carrito": productos_carrito,
        "total_carrito": total,
        "carrito_valido": carrito_valido,
    }
    return render(request, "store/carrito.html", context)



# ============================================================
# 🔄 Vista: agregar al carrito (CORREGIDA PARA IMÁGENES)
# ============================================================
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product

def agregar_al_carrito(request, product_id):
    if request.method == 'POST':
        producto = get_object_or_404(Product, id=product_id)
        
        # 1. Captura de datos enviados por AJAX
        talla = request.POST.get('talla', 'Única').strip()
        color = request.POST.get('color', 'Único').strip()
        imagen_url = request.POST.get('imagen_seleccionada_url', '').strip()

        # Respaldo: si no hay imagen seleccionada, usar la principal del producto
        if not imagen_url or imagen_url == "undefined":
            imagen_url = producto.image.url if producto.image else "/static/icons/no-image.png"

        carrito = request.session.get('carrito', {})

        # 2. LLAVE ÚNICA: ID + Talla + Color (Permite variantes separadas)
        item_key = f"{product_id}|{talla}|{color}"

        precio = float(producto.final_price)

        if item_key in carrito:
            carrito[item_key]['cantidad'] += 1
            carrito[item_key]['subtotal'] = carrito[item_key]['cantidad'] * precio
        else:
            carrito[item_key] = {
                'item_key': item_key,
                'producto_id': producto.id,
                'nombre': producto.name,
                'precio': precio,
                'talla': talla,
                'color': color,
                'imagen_url': imagen_url,
                'cantidad': 1,
                'subtotal': precio,
                'disponible': True # Asegúrate de que tu lógica de stock actualice esto
            }

        request.session['carrito'] = carrito
        request.session.modified = True
        
        return JsonResponse({
            'status': 'ok', 
            'cart_count': sum(item['cantidad'] for item in carrito.values())
        })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)


# ============================================================
# 🔄 Vista: actualizar cantidad (Mantiene la imagen)
# ============================================================
def actualizar_cantidad(request, item_key):
    carrito = request.session.get('carrito', {})
    accion = request.POST.get('accion')
    
    if item_key in carrito:
        if accion == 'sumar':
            carrito[item_key]['cantidad'] += 1
        elif accion == 'restar' and carrito[item_key]['cantidad'] > 1:
            carrito[item_key]['cantidad'] -= 1
        
        # Al actualizar cantidad, nos aseguramos de no tocar 'imagen_url' 
        # para que no se borre lo que ya estaba.
        request.session['carrito'] = carrito
        request.session.modified = True

    return redirect('store:ver_carrito') 



# ============================================================
# 🗑️ Vista: eliminar un item específico
# ============================================================
def eliminar_del_carrito(request, item_key):
    """Elimina una combinación específica de producto/talla/color."""
    carrito = request.session.get("carrito", {})
    
    if item_key in carrito:
        nombre_producto = carrito[item_key].get('nombre', 'Producto')
        del carrito[item_key]
        request.session["carrito"] = carrito
        request.session.modified = True
        messages.warning(request, f"{nombre_producto} fue eliminado del carrito.")
    else:
        messages.error(request, "El producto que intentas eliminar no existe en tu carrito.")

    # Soporte para AJAX (si usas carrito lateral o modal)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({
            "status": "ok", 
            "cart_count": sum(i["cantidad"] for i in carrito.values()),
            "message": "Producto eliminado"
        })
    
    return redirect('store:ver_carrito')
    """Muestra la página del carrito validando disponibilidad real en DB."""
    from .models import ProductVariant # Importación local para evitar ciclos
    
    carrito = request.session.get("carrito", {})
    total = Decimal("0")
    productos_carrito = []
    carrito_modificado = False

    # Copiamos las llaves para poder borrar items si es necesario sin error de iteración
    keys_to_check = list(carrito.keys())

    for key in keys_to_check:
        item = carrito[key]
        product_id = item["producto_id"]
        talla = item.get("talla", "")
        color = item.get("color", "")

        # 🔍 BUSQUEDA DE STOCK REAL EN LA NUEVA TABLA
        # Buscamos la variante específica
        variante = ProductVariant.objects.filter(
            product_id=product_id, 
            talla=talla, 
            color=color
        ).first()

        # 🚨 VALIDACIÓN PROFESIONAL
        if not variante or variante.stock <= 0:
            # Si ya no existe o no hay stock, lo marcamos para revisión o lo quitamos
            # En este caso, lo dejamos pero marcamos 'disponible': False para el HTML
            item_disponible = False
            stock_actual = 0
        else:
            item_disponible = True
            stock_actual = variante.stock
            # Si el usuario pide más de lo que hay, ajustamos su carrito al máximo disponible
            if item["cantidad"] > stock_actual:
                item["cantidad"] = stock_actual
                carrito_modificado = True

        # Cálculos de dinero
        subtotal = Decimal(item["precio"]) * item["cantidad"]
        total += subtotal
        
        productos_carrito.append({
            "item_key": key,
            "producto_id": product_id,
            "nombre": item["nombre"],
            "precio": Decimal(item["precio"]),
            "cantidad": item["cantidad"],
            "talla": talla,
            "color": color,
            "imagen": item.get("imagen", ""),
            "subtotal": subtotal,
            "disponible": item_disponible, # 👈 Nuevo: Para mostrar alerta en el HTML
            "stock_max": stock_actual      # 👈 Nuevo: Para limitar los botones +/-
        })

    # Si ajustamos cantidades por falta de stock, guardamos la sesión
    if carrito_modificado:
        request.session["carrito"] = carrito
        request.session.modified = True
        messages.warning(request, "Algunas cantidades se ajustaron por disponibilidad de stock.")

    context = {
        "carrito": productos_carrito,
        "total_carrito": total,
        "total_formateado": formatear_numero(total) if 'formatear_numero' in globals() else total,
        "carrito_vacio": len(productos_carrito) == 0
    }
    
    return render(request, "store/carrito.html", context)

# ============================================================
# 🛒 Vista: vaciar carrito
# ============================================================
def vaciar_carrito(request):
    """
    Limpia el carrito de la sesión.
    """
    request.session['carrito'] = {}
    messages.info(request, "Tu carrito fue vaciado.")
    return redirect('store:ver_carrito')

# ============================================================
# 🛒 Vista: modal de carrito (contenido dinámico)
# ============================================================
def carrito_modal(request, product_id):
    """
    Devuelve el fragmento HTML para el modal de carrito.
    Se usa en store.js con fetch() al hacer clic en el ícono 🛒.
    """
    producto = get_object_or_404(Product, id=product_id)
    return render(request, 'store/vista_carrito.html', {
        'producto': producto
    })

# ============================================================
# 🏬 Vista: tienda principal (store.html)
# ============================================================
def store(request):
    """
    Vista principal de la tienda:
    - Muestra banners dinámicos desde admin.
    - Muestra productos destacados en carrusel.
    - Permite filtros por categoría, búsqueda y ordenamiento.
    """

    # 🎯 Banners dinámicos
    banners = Banner.objects.all()

    # ⭐ Productos destacados (máx. 10 con imagen válida)
    productos_destacados = Product.objects.filter(
        destacado=True,
        is_available=True
    ).exclude(image__isnull=True).exclude(image='')[:10]

    # 📦 Productos disponibles
    productos = Product.objects.filter(is_available=True)
    categoria_actual = None

    # 📂 Filtro por categoría
    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        categoria_actual = get_object_or_404(Category, slug=category_slug)
        productos = productos.filter(category=categoria_actual)

    # 🔎 Filtro por búsqueda
    search_query = request.GET.get('q', '').strip()
    if search_query:
        productos = productos.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # 📊 Ordenamiento
    order = request.GET.get('order')
    if order == 'name':
        productos = productos.order_by('name')
    elif order == 'price':
        productos = productos.order_by('cost')
    elif order == 'price_desc':
        productos = productos.order_by('-cost')
    elif order == 'recent':
        productos = productos.order_by('-date_register')

    # 📂 Lista de categorías para menú
    categorias = Category.objects.all()

    context = {
        'banners': banners,
        'productos_destacados': productos_destacados,
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_actual,
        'search_query': search_query,
        'order': order,
    }
    return render(request, 'store/store.html', context)

# ============================================================
# 📂 Vista: productos por categoría
# ============================================================
def productos_por_categoria(request, category_slug):
    """
    Muestra listado de productos filtrado por una categoría específica.
    Si el slug es 'todos', se muestran todos los productos disponibles.
    Se usa en el menú de categorías y en la vista store.html.
    """
    if category_slug == "todos":
        productos = Product.objects.filter(is_available=True)
        categoria = None  # no hay categoría específica
    else:
        categoria = get_object_or_404(Category, slug=category_slug)
        productos = Product.objects.filter(category=categoria, is_available=True)

    context = {
        "categoria": categoria,
        "productos": productos,
        "slug": category_slug,  # útil para el template
    }
    return render(request, "store/productos_por_categoria.html", context)

# ============================================================
# 🧾 Vista: checkout (ESTABILIZADA Y ORGANIZADA)
# ============================================================
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import ProductVariant, ProductImage, Product

@login_required(login_url='/account/login/') # Sincronizado con JascEcommerce/urls.py
def checkout(request):
    carrito_data = request.session.get("carrito", {})
    
    if not carrito_data:
        return redirect('store:ver_carrito')

    items_confirmados = []
    subtotal_acumulado = Decimal("0")

    for key, it in carrito_data.items():
        p_id = it.get('producto_id')
        color_val = str(it.get('color', '')).strip()
        talla_val = str(it.get('talla', '')).strip()

        # 🔎 LÓGICA DE LA LUPA: Buscar imagen específica por color
        img_color = ProductImage.objects.filter(
            product_id=p_id, 
            color_vinculado__iexact=color_val
        ).first()

        # Si existe imagen para ese color la usa, si no, usa la del item o una por defecto
        url_imagen = img_color.image.url if img_color else it.get('imagen_url', '/static/icons/no-image.png')

        precio = Decimal(str(it.get('precio', 0)))
        cantidad = it.get('cantidad', 1)
        total_item = precio * cantidad
        subtotal_acumulado += total_item

        items_confirmados.append({
            'nombre': it.get('nombre'),
            'cantidad': cantidad,
            'precio': precio,
            'total_item': total_item,
            'talla': talla_val,
            'color': color_val,
            'imagen': url_imagen
        })

    # Cálculos finales
    iva = subtotal_acumulado * Decimal("0.19")
    total_final = subtotal_acumulado + iva

    context = {
        'items': items_confirmados,
        'subtotal': subtotal_acumulado,
        'iva': iva,
        'total': total_final,
    }
    
    return render(request, 'store/checkout.html', context)

# ============================================================
# 🧾 Vista: generar factura (VERSION FINAL - BLINDADA)
# ============================================================
@login_required(login_url='/account/login/')
def generar_factura(request):
    from .models import ProductVariant, Factura, DetalleFactura, ProductImage, Product
    from decimal import Decimal
    from django.contrib import messages

    if request.method != "POST":
        return redirect("store:checkout")

    # 1. Obtenemos el carrito directamente de la sesión (Evita el ImportError)
    carrito_session = request.session.get("carrito", {})
    if not carrito_session:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("store:ver_carrito")

    # 2. Captura de datos del formulario de envío
    nombre_cliente = request.POST.get("nombre")
    telefono = request.POST.get("telefono")
    direccion = request.POST.get("direccion")
    ciudad = request.POST.get("ciudad")
    departamento = request.POST.get("departamento")
    metodo_pago = request.POST.get("metodo_pago", "Contra Entrega")

    # 3. --- Cálculos Financieros (IVA ELIMINADO TOTALMENTE) ---
    total_final = Decimal("0")
    items_para_facturar = []

    for key, item in carrito_session.items():
        precio = Decimal(str(item.get('precio', 0)))
        cantidad = int(item.get('cantidad', 1))
        subtotal_item = precio * cantidad
        total_final += subtotal_item
        
        items_para_facturar.append({
            'id': item.get('producto_id'),
            'cantidad': cantidad,
            'subtotal': subtotal_item,
            'talla': item.get('talla', ''),
            'color': item.get('color', ''),
            'imagen_url': item.get('imagen_url')
        })

    # 🧾 4. Crear Factura Principal (El total ya no lleva IVA)
    factura = Factura.objects.create(
        usuario=request.user,
        total=total_final,
        metodo_pago=metodo_pago,
        estado_pago="Aprobado", # Sincronizado con tu alerta verde en el HTML
        nombre=nombre_cliente,
        email=request.user.email,
        telefono=telefono,
        direccion=direccion,
        ciudad=ciudad,
        departamento=departamento
    )

    # 🧾 5. Procesar cada Item y persistir la imagen (Lupa)
    for i in items_para_facturar:
        try:
            prod = Product.objects.get(id=i['id'])
        except Product.DoesNotExist:
            continue

        # Descuento de stock en variantes
        variante = ProductVariant.objects.filter(
            product=prod, 
            talla__iexact=i['talla'], 
            color__iexact=i['color']
        ).first()

        if variante and variante.stock >= i["cantidad"]:
            variante.stock -= i["cantidad"]
            variante.save()

        # Captura la imagen de la Lupa (por color) para que el resumen la muestre
        img_lupa = ProductImage.objects.filter(
            product=prod, 
            color_vinculado__iexact=i['color']
        ).first()
        
        foto_final = img_lupa.image.url if img_lupa else i['imagen_url']

        # Crear detalle de factura
        DetalleFactura.objects.create(
            factura=factura,
            producto=prod,
            cantidad=i["cantidad"],
            subtotal=i["subtotal"], 
            talla=i['talla'],
            color=i['color'],
            imagen_url=foto_final
        )

    # 🛒 6. Limpiar Carrito
    request.session["carrito"] = {}
    request.session.modified = True
    
    # 7. Redirección al template que me mostraste
    return render(request, "store/confirmacion_pago.html", {
        "factura": factura
    })
    
# ============================================================
# 🧾 Vista: ver factura
# ============================================================
@login_required(login_url='/account/login/')
def ver_factura(request, factura_id):
    """
    Permite al usuario autenticado ver una factura específica.
    Protegida: solo el dueño puede acceder.
    """
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)

    contexto = {
        "factura": factura,
        "items": factura.detalles.all(),  # ✅ usar related_name
        "subtotal": factura.total - factura.total * Decimal('0.19'),
        "iva": factura.total * Decimal('0.19'),
        "descuento": Decimal('0.00'),
        "total_final": factura.total,
        "estado_pago": factura.estado_pago,
    }
    return render(request, "store/factura_pdf.html", contexto)

# ============================================================
# 🧾 Vista: historial de facturas
# ============================================================
from django.core.paginator import Paginator

@login_required(login_url='/account/login/')
def mis_facturas(request):
    """
    Muestra el historial de compras optimizado con precarga de detalles
    y paginación profesional.
    """
    from django.core.paginator import Paginator
    from .models import Factura

    # Usamos prefetch_related('detalles') para cargar los productos de una vez
    facturas_list = Factura.objects.filter(usuario=request.user).prefetch_related('detalles').order_by('-fecha')

    # Paginación: 8 por página para que no se vea muy cargado
    paginator = Paginator(facturas_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'facturas': page_obj,
        'total_pedidos': facturas_list.count()
    }

    return render(request, 'store/mis_facturas.html', context)

# ============================================================
# 📄 Vista: generar factura en PDF
# ============================================================
def generar_factura_pdf(request, factura_id):
    """
    Genera un PDF de la factura usando ReportLab y lo devuelve como respuesta HTTP.
    """
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    detalles = DetalleFactura.objects.filter(factura=factura)

    # 🧮 Totales
    subtotal = sum(d.subtotal for d in detalles)
    ahorro_total = sum(
        (d.producto.cost - d.producto.final_price) * d.cantidad
        for d in detalles if d.producto.discount > 0
    )

    iva = Decimal("0.00")
    if factura.metodo_pago.lower() != "contra entrega" and getattr(factura, "aplica_iva", False):
        iva = subtotal * Decimal("0.19")

    total = subtotal + iva

    # 🧾 Generar PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Factura #{factura.id}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Tabla de productos
    data = [["Producto", "Talla", "Color", "Cantidad", "Precio original", "Precio unitario", "Subtotal"]]
    for d in detalles:
        data.append([
            d.producto.name,
            getattr(d, "talla", ""),
            getattr(d, "color", ""),
            d.cantidad,
            f"${d.producto.cost:.2f}",
            f"${d.producto.final_price:.2f}",
            f"${d.subtotal:.2f}",
        ])

    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Totales
    elements.append(Paragraph(f"Subtotal: ${subtotal:.2f}", styles['Normal']))
    if ahorro_total > 0:
        elements.append(Paragraph(f"Ahorro total: ${ahorro_total:.2f}", styles['Normal']))
    if iva > 0:
        elements.append(Paragraph(f"IVA: ${iva:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Total: ${total:.2f}", styles['Normal']))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="factura_{factura.id}.pdf"'
    response.write(pdf)
    return response



# ============================================================
# 🏦 Vista: simulación de pago por banco
# ============================================================
def simular_pago_banco(request):
    """
    Pantalla de simulación de pago por banco.
    """
    if request.method == "POST":
        return redirect('store:generar_factura')
    return render(request, "store/simular_pago_banco.html")

# ============================================================
# 🔐 Vista: login personalizado
# ============================================================
def login_view(request):
    mostrar_acceso = request.session.pop('mostrar_acceso_requerido', False)
    next_url = request.GET.get('next', '')
    return render(request, 'account/login.html', {
        'mostrar_acceso': mostrar_acceso,
        'next': next_url
    })


# ============================================================
# 🔢 Funciones auxiliares de formato numérico
# ============================================================
def formato_numero(valor):
    """ Ejemplo: 12345.67 → "12.345,67" """
    return f"{valor:,.2f}".replace(",", ".").replace(".", ",", 1)


def formatear_numero(valor):
    """ Ejemplo: 12345 → "12.345" """
    return f"{valor:,.0f}".replace(",", ".")

# ============================================================
# 📧 Generar y enviar factura por correo con PDF adjunto
# ============================================================

def enviar_factura_por_correo(factura, usuario, contexto=None):
    """
    Genera un PDF de la factura y lo envía por correo al usuario.
    🚫 Solo se envía si el estado de pago es 'Pagado'.
    """

    if factura.estado_pago != "Pagado":
        return None

    if contexto is None:
        subtotal = factura.total / Decimal('1.19')
        iva = factura.total - subtotal
        contexto = {
            "factura": factura,
            "subtotal": subtotal,
            "iva": iva,
            "descuento": Decimal('0.00'),
            "total_final": factura.total,
            "banco": factura.banco,
            "fecha_local": factura.fecha,
        }

    asunto = f"Factura #{factura.id} - JascShop"
    mensaje = render_to_string('emails/factura.html', contexto)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    elementos.append(Paragraph(f"<b>Factura #{factura.id}</b>", estilos['Title']))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"Cliente: {usuario.username}", estilos['Normal']))

    datos = [["Producto", "Cantidad", "Precio unitario", "Subtotal"]]
    for item in factura.detalles.all():
        precio_final = item.subtotal / item.cantidad
        datos.append([
            item.producto.name,
            str(item.cantidad),
            f"${formatear_numero(precio_final)}",
            f"${formatear_numero(item.subtotal)}"
        ])

    tabla = Table(datos)
    tabla.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    elementos.append(tabla)

    doc.build(elementos)
    buffer.seek(0)
    
    email = EmailMessage(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [usuario.email])
    email.attach(f'factura_{factura.id}.pdf', buffer.read(), 'application/pdf')
    email.send()


# ============================================================
# 👁️ Vista: vista rápida de producto
# ============================================================
@login_required(login_url='/account/login/')
def vista_rapida(request, id):
    producto = get_object_or_404(Product, id=id)
    return render(request, 'store/vista_rapida.html', {'producto': producto})

# ============================================================
# 🏦 Vista: widget de pago bancario (VERSION ESTABILIZADA)
# ============================================================
def pago_banco_widget(request):
    """Prepara el entorno de pago y asegura que el monto sea exacto."""
    factura_id = request.session.get("factura_id")
    
    if not factura_id:
        messages.error(request, "Sesión de pago expirada o no encontrada.")
        return redirect("store:ver_carrito")

    factura = Factura.objects.filter(id=factura_id).first()
    
    if not factura:
        messages.error(request, "La factura no existe en nuestra base de datos.")
        return redirect("store:ver_carrito")

    # Seguridad: Si ya está pagada, enviarlo directo a confirmación
    if factura.estado_pago == "Pagado":
        return redirect(f"{reverse('store:confirmacion_pago')}?status=APPROVED&reference={factura.id}")

    if request.method == "POST":
        banco = request.POST.get("banco")
        factura.banco = banco
        factura.save()

        # Simulación de respuesta exitosa
        redirect_url = reverse("store:confirmacion_pago")
        redirect_url += f"?status=APPROVED&reference={factura.id}"
        return redirect(redirect_url)

    # Preparación para Wompi o Pasarela Real
    # Nota: Las pasarelas suelen pedir el monto en centavos (Ej: 1000 pesos = 100000)
    monto_en_centavos = int(factura.total * 100)

    context = {
        "factura": factura,
        "public_key": getattr(settings, "WOMPI_PUBLIC_KEY", "pub_test_simulada"),
        "amount_in_cents": monto_en_centavos, # Para evitar errores de redondeo
        "amount": int(factura.total),
        "currency": "COP",
        "reference": str(factura.id),
        "redirect_url": request.build_absolute_uri(reverse("store:confirmacion_pago")),
    }
    
    return render(request, "store/pago_banco_widget.html", context)

# ============================================================
# ✅ Vista: confirmación de pago
# ============================================================
def confirmacion_pago(request):
    estado = request.GET.get("status")
    referencia = request.GET.get("reference") or request.session.get("factura_id")
    factura = Factura.objects.filter(id=referencia).first() if referencia else None

    if factura:
        if estado == "APPROVED":
            factura.estado_pago = "Pagado"
        elif estado == "DECLINED":
            factura.estado_pago = "Fallido"
        else:
            factura.estado_pago = "Pagado"

        factura.save()
        if factura.email:
            enviar_factura(factura, {"factura": factura})

        totales = calcular_totales(factura)

        contexto = {
            "factura": factura,
            "items": factura.detalles.all(),
            "subtotal": totales["subtotal"],
            "descuento": totales["ahorro_total"],
            "total_final": totales["total_final"],
            "fecha_local": localtime(factura.fecha),
        }
        return render(request, "store/factura.html", contexto)

    return render(request, "store/confirmacion_pago.html", {"estado": estado, "referencia": referencia})


def detalle_producto(request, slug):
    producto = get_object_or_404(Product, slug=slug)
    context = {
        'producto': producto,
        'colors': producto.color_list,
        'video_file': producto.video_file,
        'video_url': producto.video_url,
    }
    return render(request, 'store/detalle_producto.html', context)

# ============================================================
# 🔄 Vista: actualizar cantidad en carrito
# ============================================================
def actualizar_cantidad(request, item_key):
    carrito = request.session.get('carrito', {})
    accion = request.POST.get('accion')
    
    # Ahora buscamos directamente por la llave (que es ID|TALLA|COLOR)
    if item_key in carrito:
        if accion == 'sumar':
            carrito[item_key]['cantidad'] += 1
        elif accion == 'restar' and carrito[item_key]['cantidad'] > 1:
            carrito[item_key]['cantidad'] -= 1
        
        request.session['carrito'] = carrito
        request.session.modified = True

    return redirect('store:ver_carrito')


# views.py
from django.http import JsonResponse

def obtener_carrito_json(request):
    carrito = request.session.get("carrito", {})
    total = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())
    
    return JsonResponse({
        "carrito_completo": list(carrito.values()),
        "total_carrito": f"{total:,.0f}".replace(",", "."),
        "cart_count": sum(item['cantidad'] for item in carrito.values()),
        "status": "ok"
    })
    
# ============================================================
# 🌐 Vistas informativas
# ============================================================
def nosotros(request):
    """
    Página informativa 'Nosotros'.
    """
    return render(request, 'store/nosotros.html')


def contacto(request):
    """
    Página de contacto.
    """
    return render(request, 'store/contacto.html')

