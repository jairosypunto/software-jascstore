from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Factura, DetalleFactura
from categorias.models import Category
from django.contrib.auth.decorators import login_required

from .models import Banner, Product
from django.conf import settings

# =========================
# Utilidades internas
# =========================

def _precio_final(producto: Product) -> Decimal:
    """
    Devuelve el precio final del producto aplicando descuento.
    Usa la propiedad del modelo si existe; si no, lo calcula aquí.
    """
    try:
        # ✅ Usar la propiedad directamente, sin paréntesis
        return producto.final_price
    except AttributeError:
        # Fallback: cálculo directo por si la propiedad no existe
        discount = getattr(producto, 'discount', 0) or 0
        cost = Decimal(str(producto.cost))  # ✅ convertir a string
        if discount > 0:
            return cost * (Decimal('1') - Decimal(discount) / Decimal('100'))
        return cost


def _items_carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    subtotal_sin_desc = Decimal('0')
    subtotal_con_desc = Decimal('0')

    for pid, cantidad in carrito.items():
        producto = Product.objects.get(id=pid)

        precio_original = producto.cost  # 👈 llamado como método
        precio_final = producto.final_price # propiedad

        subtotal_original = producto.cost * cantidad
        subtotal_final = precio_final * cantidad

        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio_original': precio_original,
            'precio_final': precio_final,
            'subtotal_original': subtotal_original,
            'subtotal_final': subtotal_final,
        })

        subtotal_sin_desc += subtotal_original
        subtotal_con_desc += subtotal_final

    return items, subtotal_sin_desc, subtotal_con_desc

# =========================
# Carrito (sesiones)
# =========================

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def agregar_al_carrito(request, product_id):
    """
    Agrega un producto al carrito en sesión.
    - Lee 'cantidad' del formulario.
    - Valida disponibilidad y stock.
    - Incrementa cantidad si el producto ya estaba sin exceder stock.
    """
    if request.method != 'POST':
        return redirect('store:ver_carrito')

    producto = get_object_or_404(Product, id=product_id)

    if not producto.is_available or producto.stock <= 0:
        messages.warning(request, "Este producto no está disponible o está agotado.")
        return redirect('store:ver_carrito')

    # Lee cantidad enviada; si falta o es inválida, usa 1.
    try:
        cantidad = int(request.POST.get('cantidad', '1'))
    except ValueError:
        cantidad = 1

    # Normaliza límites
    if cantidad < 1:
        cantidad = 1
    if cantidad > producto.stock:
        cantidad = producto.stock
        messages.info(request, f"Se ajustó la cantidad al máximo disponible ({producto.stock}).")

    carrito = request.session.get('carrito', {})
    pid = str(product_id)

    cantidad_actual = int(carrito.get(pid, 0))
    nueva_cantidad = cantidad_actual + cantidad

    # No exceder stock total
    if nueva_cantidad > producto.stock:
        nueva_cantidad = producto.stock
        messages.info(
            request,
            f"Ya tenías {cantidad_actual}. Se ajustó a {producto.stock} por límite de stock."
        )

    carrito[pid] = nueva_cantidad
    request.session['carrito'] = carrito

    messages.success(request, f"Se agregó {cantidad} × {producto.name} al carrito.")
    return redirect('store:ver_carrito')


def vaciar_carrito(request):
    """Limpia el carrito de la sesión."""
    request.session['carrito'] = {}
    messages.info(request, "Tu carrito fue vaciado.")
    return redirect('store:ver_carrito')


def ver_carrito(request):
    """
    Muestra el carrito con precios, subtotales y total de unidades.
    Aplica descuentos en la UI del carrito.
    """
    items, subtotal_sin_desc, subtotal_con_desc = _items_carrito(request)
    descuento_total = subtotal_sin_desc - subtotal_con_desc
    iva = subtotal_con_desc * Decimal('0.19')
    total = subtotal_con_desc + iva

    # ✅ Nuevo: calcular total de unidades
    total_cantidad = sum(it['cantidad'] for it in items)

    context = {
        'items': items,
        'subtotal': subtotal_con_desc,
        'descuento': descuento_total,
        'iva': iva,
        'total': total,
        'total_cantidad': total_cantidad,  # 👈 agregado al contexto
    }
    return render(request, 'store/carrito.html', context)


# =========================
# Tienda y catálogo
# =========================
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


# =========================
# Checkout y pago
# =========================

def checkout(request):
    """
    Resumen previo a confirmación de pago:
    - Muestra precios unitarios, subtotales con descuento.
    - Calcula subtotal, descuento, IVA y total.
    """
    items, subtotal_sin_desc, subtotal_con_desc = _items_carrito(request)
    descuento_total = subtotal_sin_desc - subtotal_con_desc
    iva = subtotal_con_desc * Decimal('0.19')
    total = subtotal_con_desc + iva

    context = {
        'items': [
            # Simplifica estructura para el template actual
            {
                'producto': i['producto'],
                'cantidad': i['cantidad'],
                # El template usa item.subtotal; le pasamos el subtotal con descuento
                'subtotal': i['subtotal_final'],
            }
            for i in items
        ],
        'subtotal': subtotal_con_desc,
        'descuento': descuento_total,
        'iva': iva,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)


def confirmar_pago(request):
    """
    Valida método de pago y autenticación.
    Redirige al flujo adecuado (banco o generar factura).
    """
    if request.method == "POST":
        carrito = request.session.get('carrito', {})
        metodo_pago = request.POST.get('metodo_pago', 'No especificado')

        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('store:checkout')

        if metodo_pago not in ["banco", "contraentrega"]:
            messages.error(request, "Debes seleccionar un método de pago válido.")
            return redirect('store:checkout')

        # Si no está autenticado, guarda bandera y redirige a login con next
        if not request.user.is_authenticated:
            request.session['mostrar_acceso_requerido'] = True
            return redirect('/account/login/?next=/store/checkout/')
        # Persistimos datos necesarios
        request.session['carrito'] = carrito
        request.session['metodo_pago'] = metodo_pago
        # Continuación del flujo
        if metodo_pago == "banco":
            return redirect('store:simular_pago_banco')
        else:
            return redirect('store:generar_factura')
    return redirect('store:checkout')

# ✅ Vista protegida: solo usuarios autenticados pueden generar facturas
@login_required(login_url='/accounts/login/')
def generar_factura(request):
    carrito = request.session.get('carrito', {})
    metodo_pago = request.POST.get("metodo_pago") or request.session.get("metodo_pago", "No especificado")
    banco_seleccionado = request.POST.get("banco") or request.session.get("banco_seleccionado")

    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('store:checkout')

    factura = Factura.objects.create(
        usuario=request.user,
        total=Decimal('0.00'),
        metodo_pago=metodo_pago,
        banco=banco_seleccionado,  # ✅ se guarda el banco
    )
    request.session["factura_id"] = factura.id

    items_detalle = []
    subtotal_con_desc = Decimal('0')
    subtotal_sin_desc = Decimal('0')
    iva_total = Decimal('0')

    for pid_str, cantidad in carrito.items():
        producto = get_object_or_404(Product, id=int(pid_str))
        cantidad = int(cantidad)
        precio_original = Decimal(str(producto.cost))
        precio_final = _precio_final(producto)
        subtotal_original = precio_original * cantidad
        subtotal_final = precio_final * cantidad

        detalle = DetalleFactura.objects.create(
            factura=factura,
            producto=producto,
            cantidad=cantidad,
            subtotal=subtotal_final
        )
        items_detalle.append(detalle)
        subtotal_sin_desc += subtotal_original
        subtotal_con_desc += subtotal_final
        if not producto.is_tax_exempt:
            iva_total += subtotal_final * Decimal('0.19')

    descuento_total = subtotal_sin_desc - subtotal_con_desc
    total_final = subtotal_con_desc + iva_total

    estado_pago = {
        "contraentrega": "Pendiente",
        "transferencia": "Pendiente",
        "banco": "Pagado en prueba",
    }.get(metodo_pago, "No definido")

    factura.total = total_final
    factura.estado_pago = estado_pago
    factura.save()

    request.session['carrito'] = {}
    enviar_factura_por_correo(factura, request.user)  # ✅ banco incluido en correo

    contexto = {
        "factura": factura,
        "items": items_detalle,
        "subtotal": subtotal_con_desc,
        "iva": iva_total,
        "descuento": descuento_total,
        "total_final": total_final,
        "estado_pago": estado_pago,
    }
    return render(request, "store/factura.html", contexto)

# ✅ Vista protegida: solo el dueño puede ver su factura
@login_required(login_url='/accounts/login/')
def ver_factura(request, factura_id):
    # 🔍 Buscar la factura del usuario actual
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)

    # 📦 Preparar contexto con los datos de la factura
    contexto = {
        "factura": factura,
        "items": factura.detallefactura_set.all(),
        "subtotal": factura.total - factura.total * Decimal('0.19'),
        "iva": factura.total * Decimal('0.19'),
        "descuento": Decimal('0.00'),
        "total_final": factura.total,
        "estado_pago": factura.estado_pago,
    }

    # 🖥️ Renderizar plantilla PDF/HTML
    return render(request, "store/factura_pdf.html", contexto)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Factura

# ✅ Vista protegida: historial de facturas del usuario autenticado
@login_required(login_url='/accounts/login/')
def mis_facturas(request):
    # 🔍 Filtrar facturas del usuario actual
    facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha')

    # 📦 Renderizar plantilla con listado
    return render(request, 'store/mis_facturas.html', {'facturas': facturas})


def simular_pago_banco(request):
    """
    Pantalla de simulación de pago por banco.
    En un flujo real, aquí se validaría el callback de la pasarela de pagos.
    """
    if request.method == "POST":
        return redirect('store:generar_factura')
    return render(request, "store/simular_pago_banco.html")


# =========================
# Login y páginas informativas
# =========================

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

from io import BytesIO
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def formato_numero(valor):
    return f"{valor:,.2f}".replace(",", ".").replace(".", ",", 1)

def enviar_factura_por_correo(factura, usuario):
    asunto = f"Factura #{factura.id} - LatinShop"

    mensaje = render_to_string('store/factura_email.html', {
        'factura': factura,
        'subtotal': factura.total - factura.total * Decimal('0.19'),
        'iva': factura.total * Decimal('0.19'),
        'descuento': Decimal('0.00'),
        'total_final': factura.total,
        'banco': factura.banco  # ✅ se pasa al template del correo
    })

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    # Encabezado
    elementos.append(Paragraph(f"<b>Factura #{factura.id} - LatinShop</b>", estilos['Title']))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"Cliente: {usuario.username}", estilos['Normal']))
    elementos.append(Paragraph(f"Email: {usuario.email}", estilos['Normal']))
    elementos.append(Paragraph(f"Fecha: {factura.fecha}", estilos['Normal']))
    elementos.append(Paragraph(f"Método de pago: {factura.metodo_pago}", estilos['Normal']))
    elementos.append(Paragraph(f"Estado del pago: {factura.estado_pago}", estilos['Normal']))
    if factura.banco:
        elementos.append(Paragraph(f"Banco utilizado: {factura.banco}", estilos['Normal']))  # ✅ banco en PDF
    elementos.append(Spacer(1, 12))

    # Tabla de productos
    datos = [["Producto", "Cantidad", "Subtotal"]]
    for item in factura.detalles.all():
        datos.append([
            item.producto.name,
            str(item.cantidad),
            f"${formato_numero(item.subtotal)}"
        ])

    tabla = Table(datos, colWidths=[250, 100, 100])
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
    subtotal = factura.total - factura.total * Decimal('0.19')
    iva = factura.total * Decimal('0.19')
    descuento = Decimal('0.00')
    total_final = factura.total

    elementos.append(Paragraph(f"<b>Subtotal:</b> ${formato_numero(subtotal)}", estilos['Normal']))
    elementos.append(Paragraph(f"<b>IVA (19%):</b> ${formato_numero(iva)}", estilos['Normal']))
    elementos.append(Paragraph(f"<b>Descuento:</b> ${formato_numero(descuento)}", estilos['Normal']))
    elementos.append(Paragraph(f"<b>Total pagado:</b> ${formato_numero(total_final)}", estilos['Normal']))

    doc.build(elementos)
    buffer.seek(0)

    email = EmailMessage(asunto, mensaje, to=[usuario.email])
    email.content_subtype = "html"
    email.attach(f"Factura_{factura.id}.pdf", buffer.read(), 'application/pdf')
    email.send()

def vista_rapida(request, id):
    producto = get_object_or_404(Product, id=id)
    return render(request, 'store/vista_rapida.html', {'producto': producto})


@login_required(login_url='/accounts/login/')
def ver_factura(request, factura_id):
    # 🔍 Buscar la factura del usuario actual
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)

    # 📦 Preparar contexto con los datos de la factura
    contexto = {
        "factura": factura,
        "items": factura.detallefactura_set.all(),
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
        return redirect("store:confirmacion_pago")

    # 💳 Preparar contexto para el widget de pago
    context = {
        "public_key": getattr(settings, "WOMPI_PUBLIC_KEY", "pub_test_simulada"),
        "amount": int(factura.total * 100),  # centavos
        "currency": "COP",
        "reference": str(factura.id),
        "redirect_url": request.build_absolute_uri("/store/confirmacion-pago/"),
    }

    return render(request, "store/pago_banco_widget.html", context)


def confirmacion_pago(request):
    """
    Confirmación provisional:
    - Cuando conectes Wompi: usa ?id=<transaction_id> y consulta la transacción.
    - Por ahora, acepta ?status=<APPROVED|DECLINED> & reference=<id_factura>.
    """
    estado = request.GET.get("status", "SIMULADO")
    referencia = request.GET.get("reference")

    factura = None
    if referencia:
        factura = Factura.objects.filter(id=referencia).first()

    if factura:
        factura.estado = "Pagada" if estado == "APPROVED" else "Fallida"
        factura.save()

    context = {"estado": estado, "referencia": referencia}
    return render(request, "store/confirmacion_pago.html", context)


from django.shortcuts import render

def detalle_producto(request, product_id):
    producto = get_object_or_404(Product, id=product_id)
    print("Usando plantilla: detalle_producto.html")  # 👈 Esto aparecerá en consola
    return render(request, 'detalle_producto.html', {'producto': producto})


def actualizar_cantidad(request, product_id):
    """
    Actualiza la cantidad de un producto en el carrito usando botones + y –.
    """
    if request.method != 'POST':
        return redirect('store:ver_carrito')

    producto = get_object_or_404(Product, id=product_id)
    carrito = request.session.get('carrito', {})
    pid = str(product_id)
    cantidad_actual = int(carrito.get(pid, 0))

    accion = request.POST.get('accion')
    if accion == 'sumar':
        nueva = min(cantidad_actual + 1, producto.stock)
    elif accion == 'restar':
        nueva = max(cantidad_actual - 1, 1)
    else:
        nueva = cantidad_actual

    carrito[pid] = nueva
    request.session['carrito'] = carrito
    messages.success(request, f"Cantidad actualizada: {producto.name} → {nueva} und.")
    return redirect('store:ver_carrito')

# 🌐 Vista informativa de "Nosotros"
def nosotros(request):
    return render(request, 'store/nosotros.html')


def contacto(request):
    return render(request, 'store/contacto.html')
