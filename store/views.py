# ============================
# Librerías estándar de Python
# ============================
from decimal import Decimal
from io import BytesIO

# ============
# Librerías Django
# ============
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse

from django.utils.timezone import localtime

# ============
# Modelos propios
# ============
from .models import Product, Factura, DetalleFactura, Banner, Category

# ============
# Utilidades propias
# ============
from store.utils import formatear_numero

# ============
# Librerías externas (ReportLab para PDF)
# ============
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
    """
    Construye una lista de ítems del carrito desde la sesión.
    Optimizado para cargar todos los productos en un solo query.
    """
    carrito = request.session.get('carrito', {})
    items = []

    # Obtener todos los IDs de productos en el carrito
    ids = [item['producto_id'] for item in carrito.values()]
    productos = Product.objects.in_bulk(ids)  # carga masiva

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
            'talla': talla,
            'color': color,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'precio_original': precio_original,
            'discount': producto.discount,
            'subtotal': subtotal_item,
        })

    return items


# ============================================================
# 🛒 Vista: agregar producto al carrito
# ============================================================
def agregar_al_carrito(request, product_id):
    print("🔥 ENTRÓ A agregar_al_carrito")

    producto = get_object_or_404(Product, id=product_id)

    if request.method != "POST":
        return redirect("store:store")

    # 📥 Datos
    cantidad = max(1, int(request.POST.get("cantidad", 1)))
    talla = request.POST.get("selected_size_hidden", "").strip()
    color = request.POST.get("selected_color_hidden", "").strip()

    # ❌ Validación real
    if producto.talla_list and not talla:
        print("❌ ERROR: talla no enviada")
        return redirect("store:store")

    carrito = request.session.get("carrito", {})
    item_key = f"{product_id}|{talla}|{color}"

    if item_key in carrito:
        carrito[item_key]["cantidad"] += cantidad
    else:
        carrito[item_key] = {
            "producto_id": product_id,
            "nombre": producto.name,
            "precio": float(producto.final_price),
            "cantidad": cantidad,
            "talla": talla,
            "color": color,
        }

    request.session["carrito"] = carrito
    request.session.modified = True

    print("✅ AGREGADO CORRECTAMENTE:", carrito)

    return redirect("store:ver_carrito")



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
# 📋 Vista: ver carrito
# ============================================================
# ============================================================
# 📋 Vista: ver carrito
# ============================================================
def ver_carrito(request):
    carrito = request.session.get('carrito', {})

    items = []
    subtotal = 0

    for item in carrito.values():
        total_item = item['precio'] * item['cantidad']
        subtotal += total_item

        items.append({
            **item,  # incluye producto_id
            'total_item': total_item
        })

    context = {
        'items': items,
        'subtotal': subtotal,
        'total_items': sum(i['cantidad'] for i in items)
    }

    return render(request, 'store/carrito.html', context)



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
    Se usa en el menú de categorías y en la vista store.html.
    """
    categoria = get_object_or_404(Category, slug=category_slug)
    productos = Product.objects.filter(category=categoria, is_available=True)

    context = {
        'categoria': categoria,
        'productos': productos,
    }
    return render(request, 'store/productos_por_categoria.html', context)


# ============================================================
# 🧾 Vista: checkout
# ============================================================
def checkout(request):
    """
    Muestra el resumen del carrito antes de confirmar la compra.
    Calcula subtotal, descuento, IVA y total.
    """
    items = _items_carrito(request)

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


# ============================================================
# 🧾 Vista: generar factura
# ============================================================
@login_required(login_url='/accounts/login/')
def generar_factura(request):
    """
    Genera una factura a partir del carrito:
    - Valida método de pago.
    - Crea factura y detalles.
    - Reduce stock de productos.
    - Envía correo con PDF adjunto.
    """
    if request.method != "POST":
        return redirect("store:checkout")

    metodo_pago = request.POST.get("metodo_pago")
    if not metodo_pago:
        messages.error(request, "Debes seleccionar un método de pago.")
        return redirect("store:checkout")

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

    # 🧾 Crear detalles de factura
    for i in items:
        producto = i["producto"]
        talla = i.get("talla", "")
        color = i.get("color", "")

        # Validar variantes
        if producto.talla_list and talla and talla not in producto.talla_list:
            talla = ""
        if producto.color_list and color and color not in producto.color_list:
            color = ""

        # Reducir stock
        if producto.stock < i["cantidad"]:
            messages.warning(request, f"Stock insuficiente para {producto.name}.")
            continue
        producto.stock -= i["cantidad"]
        producto.save()

        DetalleFactura.objects.create(
            factura=factura,
            producto=producto,
            cantidad=i["cantidad"],
            subtotal=i["subtotal"],
            talla=talla,
            color=color
        )

    # 🧹 Vaciar carrito y guardar factura en sesión
    request.session["carrito"] = {}
    request.session["factura_id"] = factura.id

    # 📧 Enviar correo con factura
    try:
        enviar_factura_por_correo(factura, request.user, {
            "factura": factura,
            "subtotal": subtotal,
            "descuento": descuento,
            "iva": iva,
            "total_final": total_final,
            "fecha_local": factura.fecha,
        })
        messages.success(request, "Factura generada y enviada por correo.")
    except Exception as e:
        messages.warning(request, f"No se pudo enviar el correo: {e}")

    # 🏦 Redirigir según método de pago
    if metodo_pago == "banco":
        return redirect("store:pago_banco")

    # Mostrar factura directamente si es contraentrega
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

    # 🧮 Recalcular totales
    subtotal = sum(d.subtotal for d in detalles)
    descuento = sum(
        (d.producto.cost - d.producto.final_price) * d.cantidad
        for d in detalles if d.producto.discount > 0
    )
    base_imponible = subtotal - descuento
    iva = base_imponible * Decimal("0.19")
    total = base_imponible + iva

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










# ============================================================
# 🏦 Vista: simulación de pago por banco
# ============================================================
def simular_pago_banco(request):
    """
    Pantalla de simulación de pago por banco.
    En un flujo real, aquí se validaría el callback de la pasarela de pagos.
    """
    if request.method == "POST":
        # En un entorno real, aquí se procesaría la respuesta de la pasarela
        return redirect('store:generar_factura')
    return render(request, "store/simular_pago_banco.html")


# ============================================================
# 🔐 Vista: login personalizado
# ============================================================
def login_view(request):
    """
    Vista de login con soporte para mostrar mensaje de acceso requerido y next.
    - 'mostrar_acceso' se usa para indicar si el usuario intentó acceder a una vista protegida.
    - 'next_url' guarda la URL a la que debe redirigirse tras el login.
    """
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
    """
    Formatea un número con dos decimales y separador de miles estilo latino.
    Ejemplo: 12345.67 → "12.345,67"
    """
    return f"{valor:,.2f}".replace(",", ".").replace(".", ",", 1)


def formatear_numero(valor):
    """
    Formatea un número entero con separador de miles.
    Ejemplo: 12345 → "12.345"
    """
    return f"{valor:,.0f}".replace(",", ".")


# ============================================================
# 📧 Generar y enviar factura por correo con PDF adjunto
# ============================================================
def enviar_factura_por_correo(factura, usuario, contexto=None):
    """
    Genera un PDF de la factura y lo envía por correo al usuario.
    - Usa ReportLab para construir el PDF.
    - Adjunta el PDF al correo junto con una plantilla HTML.
    """
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


# ============================================================
# 👁️ Vista: vista rápida de producto
# ============================================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Product


@login_required(login_url='/accounts/login/')
def vista_rapida(request, id):
    """
    Vista rápida de producto (modal único tipo TEMU).
    - Usa UNA sola plantilla: store/vista_rapida.html
    - Maneja galería, video, tallas, colores y carrito
    """

    producto = get_object_or_404(Product, id=id)

    context = {
        'producto': producto,
        # NO necesitas pasar talla/color aparte
        # ya vienen desde producto.talla_list y producto.colors_list
    }

    return render(request, 'store/vista_rapida.html', context)






# ============================================================
# 🧾 Vista: ver factura específica
# ============================================================
def ver_factura(request, factura_id):
    """
    Permite al usuario autenticado ver una factura específica.
    Protegida: solo el dueño puede acceder.
    """
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


# ============================================================
# 🏦 Vista: widget de pago bancario (pre-Wompi)
# ============================================================
def pago_banco_widget(request):
    """
    Prepara datos y muestra el formulario que luego redirige al checkout de Wompi.
    Simula la selección de banco y redirige a confirmación de pago.
    """
    factura_id = request.session.get("factura_id")
    if not factura_id:
        messages.error(request, "No hay factura en sesión.")
        return redirect("store:ver_carrito")

    factura = Factura.objects.filter(id=factura_id).first()
    if not factura:
        messages.error(request, "La factura no existe.")
        return redirect("store:ver_carrito")

    # 🏦 Capturar banco seleccionado
    if request.method == "POST":
        banco = request.POST.get("banco")
        request.session["banco_seleccionado"] = banco
        print("🏦 Banco seleccionado:", banco)

        factura.banco = banco
        factura.save()

        # Redirigir a confirmación simulada
        redirect_url = reverse("store:confirmacion_pago")
        redirect_url += f"?status=APPROVED&reference={factura.id}"
        return redirect(redirect_url)

    # 💳 Contexto inicial para widget de pago
    context = {
        "public_key": getattr(settings, "WOMPI_PUBLIC_KEY", "pub_test_simulada"),
        "amount": int(factura.total * 100),  # centavos
        "currency": "COP",
        "reference": str(factura.id),
        "redirect_url": request.build_absolute_uri("/store/confirmacion-pago/"),
    }
    return render(request, "store/pago_banco_widget.html", context)


# ============================================================
# ✅ Vista: confirmación de pago
# ============================================================
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
        factura.estado_pago = "Pagado" if estado == "APPROVED" else "Fallido"
        fecha_local = localtime(factura.fecha)  # ✅ Hora local Colombia
        factura.save()

        items = factura.detalles.all()

        # 🧮 Calcular totales
        subtotal = sum(d.subtotal for d in items)
        iva = sum(
            d.subtotal * Decimal('0.19')
            for d in items if not d.producto.is_tax_exempt
        )
        descuento = sum(
            (d.producto.cost - d.producto.final_price) * d.cantidad
            for d in items if d.producto.discount > 0
        )
        total_final = subtotal - descuento + iva

        contexto = {
            "factura": factura,
            "items": items,
            "subtotal": subtotal,
            "iva": iva,
            "descuento": descuento,
            "total_final": total_final,
            "estado_pago": factura.estado_pago,
            "fecha_local": fecha_local,
        }
        return render(request, "store/factura.html", contexto)

    # ⚠️ Si no hay factura válida
    context = {"estado": estado, "referencia": referencia}
    return render(request, "store/confirmacion_pago.html", context)


# ============================================================
# 🛍️ Vista: detalle de producto
# ============================================================
def detalle_producto(request, slug):
    """
    Muestra detalle completo de un producto:
    - Imagen, descripción, variantes (colores, tallas).
    - Video asociado si existe.
    """
    producto = get_object_or_404(Product, slug=slug)
    print("Usando plantilla: detalle_producto.html")  # Debug

    context = {
        'producto': producto,
        'colors': producto.color_list,  # ✅ usar propiedad del modelo
        'video_file': producto.video_file,
        'video_url': producto.video_url,
    }
    return render(request, 'store/detalle_producto.html', context)


# ============================================================
# 🔄 Vista: actualizar cantidad en carrito
# ============================================================
def actualizar_cantidad(request, product_id):
    """
    Actualiza la cantidad de un producto en el carrito:
    - accion=sumar → incrementa cantidad.
    - accion=restar → decrementa cantidad (mínimo 1).
    """
    carrito = request.session.get('carrito', {})
    accion = request.POST.get('accion')

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