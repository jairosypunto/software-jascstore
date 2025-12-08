# Librerías estándar de Python
from decimal import Decimal
from io import BytesIO

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse

# Modelos propios
from .models import Product, Factura, DetalleFactura, Banner
from categorias.models import Category

# Utilidades propias
from store.utils import formatear_numero

# ReportLab (para PDF)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def _precio_final(producto: Product) -> Decimal:
    """
    Devuelve el precio final del producto aplicando descuento.
    Usa la propiedad del modelo si existe; si no, lo calcula aquí.
    """
    try:
        return producto.final_price  # ✅ propiedad del modelo
    except AttributeError:
        discount = getattr(producto, 'discount', 0) or 0
        cost = Decimal(str(producto.cost))
        if discount > 0:
            return cost * (Decimal('1') - Decimal(discount) / Decimal('100'))
        return cost
    
# 🛒 Función auxiliar optimizada para construir lista de ítems del carrito
def _items_carrito(request):
    carrito = request.session.get('carrito', {})
    items = []

    # Obtener todos los IDs de productos en el carrito
    ids = [item['producto_id'] for item in carrito.values()]
    # Cargar todos los productos en un solo query
    productos = Product.objects.in_bulk(ids)

    for key, item in carrito.items():
        producto = productos.get(item['producto_id'])
        if not producto:
            continue  # Si el producto no existe, saltar

        cantidad = item['cantidad']
        talla = item.get('talla', '')
        color = item.get('color', '')

        precio_original = producto.cost
        precio_unitario = producto.final_price
        subtotal_item = precio_unitario * cantidad

        # Diccionario que representa un ítem del carrito
        items.append({
            'producto': producto,
            'size': talla,
            'color': color,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'precio_original': precio_original,
            'discount': producto.discount,
            'subtotal': subtotal_item,
        })

    return items


def agregar_al_carrito(request, product_id):
    producto = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        talla = request.POST.get('selected_size', '')
        color = request.POST.get('selected_color', '')

        # 🔎 Validación inmediata en consola
        print(">>> DEBUG talla:", talla)
        print(">>> DEBUG color:", color)

        carrito = request.session.get('carrito', {})
        item_key = f"{product_id}_{talla}_{color}"

        carrito[item_key] = {
            'producto_id': product_id,
            'cantidad': cantidad,
            'talla': talla,
            'color': color,
        }

        request.session['carrito'] = carrito
        print(f"[DEBUG] Producto agregado: {producto.name}, cantidad: {cantidad}, talla: {talla}, color: {color}")
        print(">>> DEBUG carrito:", request.session['carrito'])  # 👈 Aquí ves todo el diccionario

    return redirect('store:ver_carrito')

def vaciar_carrito(request):
    """Limpia el carrito de la sesión."""
    request.session['carrito'] = {}
    messages.info(request, "Tu carrito fue vaciado.")
    return redirect('store:ver_carrito')

# 📋 Vista para mostrar el carrito
def ver_carrito(request):
    items = _items_carrito(request)  # Usamos la función auxiliar

    subtotal = sum(i['subtotal'] for i in items)
    descuento_total = sum(
        (i['precio_original'] - i['precio_unitario']) * i['cantidad']
        for i in items if i['discount'] > 0
    )
    base_imponible = subtotal - descuento_total
    iva = base_imponible * Decimal("0.19")
    total = base_imponible + iva
    total_cantidad = sum(i['cantidad'] for i in items)

    context = {
        'items': items,
        'subtotal': subtotal,
        'descuento': descuento_total,
        'iva': iva,
        'total': total,
        'total_cantidad': total_cantidad,
    }
    return render(request, 'store/carrito.html', context)

def store(request):
    """
    Listado de productos:
    - Productos destacados (con imagen válida)
    - Filtros: categoría, búsqueda
    - Ordenamiento: nombre, precio, precio desc, reciente
    - Banner dinámico desde admin
    """

    # Productos destacados para carrusel
    # Banner dinámico
    banner = Banner.objects.first()

    # Destacados para carrusel
    banners = Banner.objects.all()
    productos_destacados = Product.objects.filter(
        destacado=True,
        is_available=True
    ).exclude(image__isnull=True).exclude(image='')[:10]

    productos = Product.objects.filter(is_available=True)
    categoria_actual = None

    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        categoria_actual = get_object_or_404(Category, slug=category_slug)
        productos = productos.filter(category=categoria_actual)

    # Filtro por búsqueda (validación extra para evitar errores con espacios o símbolos)
    search_query = request.GET.get('q', '').strip()
    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    order = request.GET.get('order')
    if order == 'name':
        productos = productos.order_by('name')
    elif order == 'price':
        productos = productos.order_by('cost')
    elif order == 'price_desc':
        productos = productos.order_by('-cost')
    elif order == 'recent':
        productos = productos.order_by('-date_register')

    # Lista de categorías para el menú
    categorias = Category.objects.all()

    context = {
        'banners': banners,
        'productos_destacados': productos_destacados,
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_actual,
        'search_query': search_query,  # útil para mantener el texto en el input
        'order': order,  # útil para mantener el orden seleccionado
    }
    return render(request, 'store/store.html', context)

def productos_por_categoria(request, category_slug):
    """Listado de productos filtrado por una categoría específica."""
    categoria = get_object_or_404(Category, slug=category_slug)
    productos = Product.objects.filter(category=categoria, is_available=True)
    context = {
        'categoria': categoria,
        'productos': productos,
    }
    return render(request, 'store/productos_por_categoria.html', context)

# 🧾 Vista de checkout
def checkout(request):
    items = _items_carrito(request)  # Reutilizamos la función auxiliar

    subtotal = sum(i['subtotal'] for i in items)
    descuento_total = sum(
        (i['precio_original'] - i['precio_unitario']) * i['cantidad']
        for i in items if i['discount'] > 0
    )
    base_imponible = subtotal - descuento_total
    iva = base_imponible * Decimal("0.19")
    total = base_imponible + iva
    total_cantidad = sum(i['cantidad'] for i in items)

    context = {
        'items': items,
        'subtotal': subtotal,
        'iva': iva,
        'descuento': descuento_total,
        'total': total,
        'total_cantidad': total_cantidad,
    }
    return render(request, 'store/checkout.html', context)

from .views import _items_carrito  # 👈 reutilizamos la función auxiliar

# 🧾 Generar factura a partir del carrito
@login_required(login_url='/accounts/login/')
def generar_factura(request):
    # 🚦 Validar método
    if request.method != "POST":
        return redirect("store:checkout")

    # 🚦 Validar método de pago
    metodo_pago = request.POST.get("metodo_pago")
    if not metodo_pago:
        messages.error(request, "Debes seleccionar un método de pago.")
        return redirect("store:checkout")

    # 🛒 Obtener ítems del carrito
    items = _items_carrito(request)
    if not items:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("store:ver_carrito")

    # 🧮 Cálculos globales
    subtotal = sum(i["subtotal"] for i in items)
    descuento = sum(
        (i["precio_original"] - i["precio_unitario"]) * i["cantidad"]
        for i in items if i["discount"] > 0
    )
    base_imponible = subtotal - descuento
    iva = base_imponible * Decimal("0.19")
    total_final = base_imponible + iva

    # 🧾 Crear factura principal
    factura = Factura.objects.create(
        usuario=request.user,
        total=total_final,
        metodo_pago=metodo_pago,
        estado_pago="Pendiente"
    )

    # 🧾 Crear detalles de factura (líneas de productos)
    for i in items:
        DetalleFactura.objects.create(
            factura=factura,
            producto=i["producto"],
            cantidad=i["cantidad"],
            subtotal=i["subtotal"],  # subtotal de la línea
            talla=i.get("size", ""),  # variante seleccionada
            color=i.get("color", "")  # variante seleccionada
        )

    # 🧹 Vaciar carrito y guardar factura en sesión
    request.session["carrito"] = {}
    request.session["factura_id"] = factura.id

    # 📧 Enviar correo con factura y PDF adjunto
    try:
        enviar_factura_por_correo(factura, request.user, {
            "factura": factura,
            "subtotal": subtotal,
            "descuento": descuento,
            "iva": iva,
            "total_final": total_final,
            # ⚠️ Validar si existe campo banco en Factura antes de usarlo
            "fecha_local": factura.fecha,
        })
    except Exception as e:
        # ⚠️ Si falla el envío, mostrar mensaje pero no romper el flujo
        messages.warning(request, f"No se pudo enviar el correo: {e}")

    # 🏦 Redirigir si el método es banco
    if metodo_pago == "banco":
        return redirect("store:pago_banco")

    # 🧾 Mostrar factura directamente si es contraentrega
    context = {
        "factura": factura,
        "items": items,
        "subtotal": subtotal,
        "descuento": descuento,
        "iva": iva,
        "total_final": total_final,
        "estado_pago": factura.estado_pago,
    }
    return render(request, "store/factura_detalle.html", context)


# ✅ Vista protegida: solo el dueño puede ver su factura
@login_required(login_url='/accounts/login/')
def ver_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)

    contexto = {
        "factura": factura,
        "items": factura.detalles.all(),  # ✅ usar el related_name correcto
        "subtotal": factura.total - factura.total * Decimal('0.19'),
        "iva": factura.total * Decimal('0.19'),
        "descuento": Decimal('0.00'),
        "total_final": factura.total,
        "estado_pago": factura.estado_pago,
    }

    return render(request, "store/factura_pdf.html", contexto)

# ✅ Vista protegida: historial de facturas del usuario autenticado
@login_required(login_url='/accounts/login/')
def mis_facturas(request):
    # 🔍 Filtrar facturas del usuario actual
    facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha')

    # 📦 Renderizar plantilla con listado
    return render(request, 'store/mis_facturas.html', {'facturas': facturas})

# 📄 Generar factura en PDF y devolverla como respuesta HTTP
def generar_factura_pdf(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    detalles = DetalleFactura.objects.filter(factura=factura)

    # 🧮 Recalcular subtotal, descuento, IVA
    subtotal = sum(d.subtotal for d in detalles)
    descuento = sum(
        (d.producto.cost - d.producto.final_price) * d.cantidad
        for d in detalles if d.producto.discount > 0
    )
    base_imponible = subtotal - descuento
    iva = base_imponible * Decimal("0.19")
    total = base_imponible + iva

    # 🧾 Generar PDF con ReportLab
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Encabezado
    elements.append(Paragraph(f"Factura #{factura.id}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Tabla de productos con talla, color y precios
    data = [["Producto", "Talla", "Color", "Cantidad", "Precio original", "Precio unitario", "Subtotal"]]
    for d in detalles:
        precio_original = d.producto.cost
        precio_unitario = d.producto.final_price
        subtotal_linea = d.total

        data.append([
            d.producto.nombre,
            getattr(d, "talla", ""),   # si tienes campo talla
            getattr(d, "color", ""),   # si tienes campo color
            d.cantidad,
            f"${precio_original:.2f}",
            f"${precio_unitario:.2f}",
            f"${subtotal_linea:.2f}",
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
    elements.append(Paragraph(f"Descuento: ${descuento:.2f}", styles['Normal']))
    elements.append(Paragraph(f"IVA: ${iva:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Total: ${total:.2f}", styles['Normal']))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    # Respuesta HTTP con PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="factura_{factura.id}.pdf"'
    response.write(pdf)
    return response

def simular_pago_banco(request):
    """
    Pantalla de simulación de pago por banco.
    En un flujo real, aquí se validaría el callback de la pasarela de pagos.
    """
    if request.method == "POST":
        return redirect('store:generar_factura')
    return render(request, "store/simular_pago_banco.html")

def login_view(request):
    """
    Vista de login con soporte para mostrar mensaje de acceso requerido y next.
    """
    mostrar_acceso = request.session.pop('mostrar_acceso_requerido', False)
    next_url = request.GET.get('next', '')
    return render(request, 'account/login.html', {
        'mostrar_acceso': mostrar_acceso,
        'next': next_url
    })

def formato_numero(valor):
    return f"{valor:,.2f}".replace(",", ".").replace(".", ",", 1)

# Función auxiliar para formatear números con separador de miles
def formatear_numero(valor):
    return f"{valor:,.0f}".replace(",", ".")

# 📧 Generar y enviar factura por correo con PDF adjunto
def enviar_factura_por_correo(factura, usuario, contexto=None):
    # Si no se pasa contexto, calcular totales básicos
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

    # Asunto y cuerpo del correo
    asunto = f"Factura #{factura.id} - JascShop"
    mensaje = render_to_string('emails/factura.html', contexto)

    # Buffer para PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    # Encabezado de la factura
    elementos.append(Paragraph(f"<b>Factura #{factura.id} - JascShop</b>", estilos['Title']))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"Cliente: {usuario.username}", estilos['Normal']))
    elementos.append(Paragraph(f"Email: {usuario.email}", estilos['Normal']))
    elementos.append(Paragraph(f"Fecha: {contexto['fecha_local']}", estilos['Normal']))
    elementos.append(Paragraph(f"Método de pago: {factura.metodo_pago}", estilos['Normal']))
    elementos.append(Paragraph(f"Estado del pago: {factura.estado_pago}", estilos['Normal']))
    if factura.banco:
        elementos.append(Paragraph(f"Banco utilizado: {factura.banco}", estilos['Normal']))
    elementos.append(Spacer(1, 12))

    # Tabla de productos
    datos = [["Producto", "Cantidad", "Precio unitario", "Subtotal"]]
    for item in factura.detalles.all():
        precio_final = item.subtotal / item.cantidad
        precio_original = Decimal(item.producto.cost)
        texto_precio = f"${formatear_numero(precio_final)}"
        if item.producto.discount > 0:
            texto_precio += f" (antes ${formatear_numero(precio_original)})"

        # 👇 Incluir talla y color en el nombre del producto
        nombre_producto = item.producto.name
        if item.talla or item.color:
            variantes = []
            if item.talla:
                variantes.append(f"Talla: {item.talla}")
            if item.color:
                variantes.append(f"Color: {item.color}")
            nombre_producto += f" ({' | '.join(variantes)})"

        datos.append([
            nombre_producto,
            str(item.cantidad),
            texto_precio,
            f"${formatear_numero(item.subtotal)}"
        ])

    tabla = Table(datos, colWidths=[250, 80, 100, 100])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 12))

    # Totales
    elementos.append(Paragraph(f"<b>Subtotal:</b> ${formatear_numero(contexto['subtotal'])}", estilos['Normal']))
    elementos.append(Paragraph(f"<b>IVA (19%):</b> ${formatear_numero(contexto['iva'])}", estilos['Normal']))
    elementos.append(Paragraph(f"<b>Descuento:</b> ${formatear_numero(contexto['descuento'])}", estilos['Normal']))
    elementos.append(Paragraph(f"<b>Total pagado:</b> ${formatear_numero(contexto['total_final'])}", estilos['Normal']))

    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)

    # Crear y enviar correo con PDF adjunto
    email = EmailMessage(
        asunto,
        mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email]
    )
    email.content_subtype = "html"
    email.attach(f"Factura_{factura.id}.pdf", buffer.read(), 'application/pdf')
    email.send()

def vista_rapida(request, id):
    producto = get_object_or_404(Product, id=id)
    context = {
        'producto': producto,
        'sizes': producto.sizes_list,
        'colors': producto.colors_list,
    }
    return render(request, 'store/vista_rapida.html', context)
@login_required(login_url='/accounts/login/')

def ver_factura(request, factura_id):
    # 🔍 Buscar la factura del usuario actual
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)

    # 📦 Preparar contexto con los datos de la factura
    contexto = {
        "factura": factura,
        "items": factura.detalles.all(),  # ✅ usar el related_name correcto
        "subtotal": factura.total - factura.total * Decimal('0.19'),
        "iva": factura.total * Decimal('0.19'),
        "descuento": Decimal('0.00'),
        "total_final": factura.total,
        "estado_pago": factura.estado_pago,
    }

    # 🖥️ Renderizar plantilla PDF/HTML
    return render(request, "store/factura_pdf.html", contexto)


# ✅ Vista 'pre-Wompi': prepara datos y muestra el formulario que luego redirigirá al checkout de Wompi
def pago_banco_widget(request):
    # 🧾 Obtener factura desde la sesión
    factura_id = request.session.get("factura_id")
    if not factura_id:
        messages.error(request, "No hay factura en sesión.")
        return redirect("store:ver_carrito")

    factura = Factura.objects.filter(id=factura_id).first()
    if not factura:
        messages.error(request, "La factura no existe.")
        return redirect("store:ver_carrito")

    # 🏦 Capturar banco seleccionado si se envió por POST
    if request.method == "POST":
        banco = request.POST.get("banco")
        request.session["banco_seleccionado"] = banco
        print("🏦 Banco seleccionado:", banco)

        # ✅ Guardar banco en la factura
        factura.banco = banco
        factura.save()

        # ✅ Redirigir directamente a confirmación simulada
        redirect_url = reverse("store:confirmacion_pago")
        redirect_url += f"?status=APPROVED&reference={factura.id}"
        return redirect(redirect_url)

    # 💳 Preparar contexto inicial para el widget de pago
    context = {
        "public_key": getattr(settings, "WOMPI_PUBLIC_KEY", "pub_test_simulada"),
        "amount": int(factura.total * 100),  # centavos
        "currency": "COP",
        "reference": str(factura.id),
        "redirect_url": request.build_absolute_uri("/store/confirmacion-pago/"),
    }

    return render(request, "store/pago_banco_widget.html", context)
from django.utils.timezone import localtime

def confirmacion_pago(request):
    """
    Confirmación provisional:
    - Cuando conectes Wompi: usa ?id=<transaction_id> y consulta la transacción.
    - Por ahora, acepta ?status=<APPROVED|DECLINED> & reference=<id_factura>.
    """
    estado = request.GET.get("status", "SIMULADO")
    referencia = request.GET.get("reference")

    factura = Factura.objects.filter(id=referencia).first() if referencia else None

    if factura:
        factura.estado = "Pagada" if estado == "APPROVED" else "Fallida"
        fecha_local = localtime(factura.fecha)  # ✅ Hora local Colombia
        factura.save()

        # ✅ Recuperar detalles de factura
        items = factura.detalles.all()

        # 🧮 Calcular totales
        subtotal = sum(d.subtotal for d in items)
        iva = sum(
            d.subtotal * Decimal('0.19')
            for d in items
            if not d.producto.is_tax_exempt
        )
        descuento = sum(
            (Decimal(d.producto.cost) - _precio_final(d.producto)) * d.cantidad
            for d in items
        )
        total_final = subtotal + iva  # ✅ Incluye descuento

        contexto = {
            "factura": factura,
            "items": items,
            "subtotal": subtotal,
            "iva": iva,
            "descuento": descuento,
            "total_final": total_final,
            "estado_pago": factura.estado_pago,
            "fecha_local": fecha_local,  # ✅ hora local para el PDF

        }
        return render(request, "store/factura.html", contexto)

    # ⚠️ Si no hay factura válida, mostrar mensaje genérico
    context = {"estado": estado, "referencia": referencia}
    return render(request, "store/confirmacion_pago.html", context)


# 🧾 Vista para mostrar detalle de un producto
def detalle_producto(request, slug):
    # Buscar el producto por su slug
    producto = get_object_or_404(Product, slug=slug)
    print("Usando plantilla: detalle_producto.html")  # Debug en consola

    # Contexto que se pasa a la plantilla
    context = {
        'producto': producto,
        # Convertimos los campos de texto en listas usando las propiedades del modelo
        'sizes': producto.sizes_list if hasattr(producto, 'sizes_list') else [],
        'colors': producto.colors_list if hasattr(producto, 'colors_list') else [],
        'video_file': producto.video_file,
        'video_url': producto.video_url,
    }
    return render(request, 'store/detalle_producto.html', context)

def actualizar_cantidad(request, product_id):
    carrito = request.session.get('carrito', {})
    accion = request.POST.get('accion')

    # Buscar la clave correcta que contiene el product_id
    clave_encontrada = None
    for key, item in carrito.items():
        if isinstance(item, dict) and item.get('producto_id') == product_id:
            clave_encontrada = key
            break

    if clave_encontrada:
        item = carrito[clave_encontrada]
        cantidad_actual = item.get('cantidad', 1)

        if accion == 'sumar':
            item['cantidad'] = cantidad_actual + 1
        elif accion == 'restar' and cantidad_actual > 1:
            item['cantidad'] = cantidad_actual - 1

        carrito[clave_encontrada] = item
        request.session['carrito'] = carrito
        print(f"[DEBUG] Cantidad actualizada: {item['producto_id']} → {item['cantidad']} und.")
    else:
        print(f"[WARN] No se encontró el producto {product_id} en el carrito.")

    return redirect('store:ver_carrito')

# 🌐 Vista informativa de "Nosotros"
def nosotros(request):
    return render(request, 'store/nosotros.html')


def contacto(request):
    return render(request, 'store/contacto.html')
