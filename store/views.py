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
from .models import Product, Factura, DetalleFactura, Banner, Category
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
    """Construye la lista de ítems manteniendo la imagen y variantes de la sesión."""
    carrito = request.session.get('carrito', {})
    items = []
    ids = [item['producto_id'] for item in carrito.values()]
    productos_db = Product.objects.in_bulk(ids)

    for key, item in carrito.items():
        producto = productos_db.get(item['producto_id'])
        if not producto:
            continue

        precio_unitario = Decimal(str(item.get('precio', 0)))
        cantidad = int(item.get('cantidad', 0))
        
        # Recuperamos la imagen específica de la variante guardada en la sesión
        # Si por algún motivo no está, usamos la del producto por defecto
        imagen_url = item.get('imagen') or (producto.image.url if producto.image else "")

        items.append({
            'producto_id': item['producto_id'],
            'item_key': key,
            'nombre': item.get('nombre', producto.name),
            'talla': item.get('talla', ''),
            'color': item.get('color', ''),
            'cantidad': cantidad,
            'precio': precio_unitario,  # Cambiado de 'precio_unitario' para coincidir con tu HTML
            'imagen': imagen_url,
            'total_item': precio_unitario * cantidad, # Cambiado para coincidir con tu HTML
            'producto': producto,
        })
    return items



# ============================================================
# 📋 Ver carrito (Corregido)
# ============================================================

def ver_carrito(request):
    """Vista del carrito con validación completa de totales e imágenes."""
    items = _items_carrito(request)
    
    # Objeto fake para reutilizar la lógica de calcular_totales
    class DetalleFake:
        def __init__(self, it):
            self.producto = it['producto']
            self.cantidad = it['cantidad']
            self.subtotal = it['total_item']

    factura_fake = type("FacturaFake", (), {"detalles": []})()
    factura_fake.detalles = [DetalleFake(i) for i in items]
    
    totales = calcular_totales(factura_fake)

    context = {
        'items': items,
        'subtotal': totales.get('subtotal', 0),
        'descuento': totales.get('ahorro_total', 0),
        'iva': totales.get('iva', 0),
        'total_final': totales.get('total_final', 0),
        'total_items': sum(i['cantidad'] for i in items)
    }
    return render(request, 'store/carrito.html', context)



@require_POST
def agregar_al_carrito(request, product_id):
    producto = get_object_or_404(Product, id=product_id)

    # 1. Recibimos los 3 datos del formulario
    talla = request.POST.get("selected_size_hidden", "")
    color = request.POST.get("selected_color_hidden", "")
    imagen_url = request.POST.get("imagen_seleccionada_url", "")

    carrito = request.session.get("carrito", {})
    
    # Llave única por variante
    item_key = f"{product_id}|{talla}|{color}"

    if item_key not in carrito:
        precio = producto.final_price
        # Si el JS no mandó imagen por algún error, usamos la del producto
        foto_final = imagen_url if imagen_url else (producto.image.url if producto.image else "")

        carrito[item_key] = {
            "producto_id": product_id,
            "nombre": producto.name,
            "precio": str(precio),
            "cantidad": 0,
            "talla": talla,
            "color": color,
            "imagen": foto_final, # <-- ESTO ES LO QUE VERÁ EL RESUMEN
        }
    
    carrito[item_key]["cantidad"] += 1
    request.session["carrito"] = carrito
    request.session.modified = True

    # 🟢 CONSTRUCCIÓN DE RESPUESTA PARA SIDE CART JS
    lista_completa = []
    total_acumulado = Decimal("0")
    for key, val in carrito.items():
        sub = Decimal(val["precio"]) * val["cantidad"]
        total_acumulado += sub
        lista_completa.append({
            "nombre": val["nombre"],
            "talla": val["talla"],
            "color": val["color"],
            "cantidad": val["cantidad"],
            "precio_formateado": formatear_numero(Decimal(val["precio"])),
            "imagen_url": val["imagen"],
        })

    return JsonResponse({
        "status": "ok",
        "cart_count": sum(i["cantidad"] for i in carrito.values()),
        "total_carrito": formatear_numero(total_acumulado),
        "carrito_completo": lista_completa
    })

# ============================================================
# 🔄 Actualizar cantidad (NUEVA FUNCIÓN)
# ============================================================
@require_POST
def actualizar_cantidad(request):
    """
    Suma o resta cantidad desde la vista del carrito.
    """
    item_key = request.POST.get('item_key')
    action = request.POST.get('action')
    carrito = request.session.get('carrito', {})

    if item_key in carrito:
        if action == 'add':
            carrito[item_key]['cantidad'] += 1
        elif action == 'remove':
            carrito[item_key]['cantidad'] -= 1
            if carrito[item_key]['cantidad'] <= 0:
                del carrito[item_key]
        
        request.session['carrito'] = carrito
        request.session.modified = True

    return redirect('store:ver_carrito')

# ============================================================
# 📋 Ver carrito
# ============================================================



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
# 🧾 Vista: checkout
# ============================================================
def checkout(request):
    """Vista de pago corregida para evitar KeyError."""
    items = _items_carrito(request)
    if not items:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('store:ver_carrito')

    # CORRECCIÓN: Usamos 'total_item' que es lo que genera _items_carrito
    # Esto elimina el KeyError en el servidor
    subtotal_puro = sum(item['total_item'] for item in items)
    
    # Usamos el helper de totales para ser consistentes
    class DetalleFake:
        def __init__(self, it):
            self.producto = it['producto']
            self.cantidad = it['cantidad']
            self.subtotal = it['total_item']

    factura_fake = type("FacturaFake", (), {"detalles": []})()
    factura_fake.detalles = [DetalleFake(i) for i in items]
    totales = calcular_totales(factura_fake)

    context = {
        'items': items,
        'subtotal': totales.get('subtotal', 0),
        'descuento': totales.get('ahorro_total', 0),
        'iva': totales.get('iva', 0),
        'total': totales.get('total_final', 0), # Cambiado a 'total' para tu HTML
    }
    return render(request, 'store/checkout.html', context)

# ============================================================
# 🧾 Vista: generar factura (actualizada con datos de envío)
# ============================================================
@login_required(login_url='/accounts/login/')
def generar_factura(request):
    """
    Genera una factura a partir del carrito:
    - Usa 'total_item' y 'precio' para evitar KeyErrors.
    - Mantiene variantes de color/talla e imágenes.
    - Reduce stock y envía correo.
    """
    if request.method != "POST":
        return redirect("store:checkout")

    metodo_pago = request.POST.get("metodo_pago")
    if not metodo_pago:
        messages.error(request, "Debes seleccionar un método de pago.")
        return redirect("store:checkout")

    # Obtenemos los items con el nuevo formato (total_item, precio, etc.)
    items = _items_carrito(request)
    if not items:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("store:ver_carrito")

    # 🧮 Calcular totales usando las nuevas llaves del diccionario
    # Usamos 'total_item' en lugar de 'subtotal' para evitar el KeyError
    subtotal_carrito = sum(i["total_item"] for i in items)
    
    # Calculamos descuento basado en la diferencia de precios si existe
    descuento = sum(
        (i["precio_original"] - i["precio"]) * i["cantidad"]
        for i in items if i.get("discount", 0) > 0
    )
    
    iva = Decimal("0.00")
    if getattr(settings, "IVA_ACTIVO", False):
        iva = subtotal_carrito * Decimal("0.19")
    
    total_final = subtotal_carrito + iva

    # ✅ Captura de datos de envío del formulario
    nombre = request.POST.get("nombre")
    email = request.POST.get("email")
    telefono = request.POST.get("telefono")
    direccion = request.POST.get("direccion")
    ciudad = request.POST.get("ciudad")
    departamento = request.POST.get("departamento")

    # 🧾 Crear factura principal en la base de datos
    factura = Factura.objects.create(
        usuario=request.user,
        total=total_final,
        metodo_pago=metodo_pago,
        estado_pago="Pendiente",
        banco="Banco de prueba" if metodo_pago == "banco" else None,
        nombre=nombre,
        email=email,
        telefono=telefono,
        direccion=direccion,
        ciudad=ciudad,
        departamento=departamento
    )

    # 🧾 Crear detalles de la factura y actualizar Stock
    for i in items:
        producto = i["producto"]
        talla = i.get("talla", "")
        color = i.get("color", "")

        # Verificación de Stock
        if producto.stock < i["cantidad"]:
            messages.warning(request, f"Stock insuficiente para {producto.name}. Se procesará lo disponible.")
            # Opcional: podrías cancelar la operación aquí si es crítico
        
        producto.stock -= i["cantidad"]
        producto.save()

        # Guardamos el detalle con el subtotal correcto ('total_item')
        DetalleFactura.objects.create(
            factura=factura,
            producto=producto,
            cantidad=i["cantidad"],
            subtotal=i["total_item"], 
            talla=talla,
            color=color
        )

    # 🛒 Limpiar sesión
    request.session["carrito"] = {}
    request.session["factura_id"] = factura.id

    # 📨 Envío de Email
    try:
        enviar_factura(factura, {
            "factura": factura,
            "items": items,
            "subtotal": subtotal_carrito,
            "descuento": descuento,
            "iva": iva,
            "total_final": total_final,
            "fecha_local": localtime(factura.fecha),
        })
        messages.success(request, "Pedido confirmado. Se ha enviado un correo con el detalle.")
    except Exception as e:
        messages.warning(request, f"Pedido guardado, pero no se pudo enviar el correo: {e}")

    # 🔀 Redirección según el pago
    if metodo_pago == "banco":
        return redirect("store:pago_banco_widget") # O tu vista de banco específica

    # 📄 Mostrar resumen final al cliente
    context = {
        "factura": factura,
        "items": items,
        "subtotal": subtotal_carrito,
        "descuento": descuento,
        "iva": iva,
        "total_final": total_final,
    }
    return render(request, "store/factura_detalle.html", context)




# ============================================================
# 🧾 Vista: ver factura
# ============================================================
@login_required(login_url='/accounts/login/')
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
@login_required(login_url='/accounts/login/')
def mis_facturas(request):
    """
    Muestra todas las facturas del usuario autenticado.
    """
    facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'store/mis_facturas.html', {'facturas': facturas})


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
@login_required(login_url='/accounts/login/')
def vista_rapida(request, id):
    producto = get_object_or_404(Product, id=id)
    return render(request, 'store/vista_rapida.html', {'producto': producto})

# ============================================================
# 🏦 Vista: widget de pago bancario (pre-Wompi)
# ============================================================
def pago_banco_widget(request):
    factura_id = request.session.get("factura_id")
    if not factura_id:
        messages.error(request, "No hay factura en sesión.")
        return redirect("store:ver_carrito")

    factura = Factura.objects.filter(id=factura_id).first()
    if not factura:
        return redirect("store:ver_carrito")

    if request.method == "POST":
        banco = request.POST.get("banco")
        factura.banco = banco
        factura.save()

        redirect_url = reverse("store:confirmacion_pago")
        redirect_url += f"?status=APPROVED&reference={factura.id}"
        return redirect(redirect_url)

    context = {
        "public_key": getattr(settings, "WOMPI_PUBLIC_KEY", "pub_test_simulada"),
        "amount": int(factura.total),
        "currency": "COP",
        "reference": str(factura.id),
        "redirect_url": request.build_absolute_uri("/store/confirmacion-pago/"),
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