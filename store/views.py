from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Factura, DetalleFactura
from categorias.models import Category
from django.contrib.auth.decorators import login_required

from .models import Banner, Product

# =========================
# Utilidades internas
# =========================

def _precio_final(producto: Product) -> Decimal:
    """
    Devuelve el precio final del producto aplicando descuento.
    Usa el método del modelo si existe; si no, lo calcula aquí.
    """
    try:
        # Preferimos el método del modelo, más claro y reusable
        return producto.final_price()
    except AttributeError:
        # Fallback: cálculo directo por si el método no existe
        discount = getattr(producto, 'discount', 0) or 0
        cost = Decimal(str(producto.cost))          # ✅ convertir a string
        if discount > 0:
            return cost * (Decimal('1') - Decimal(discount) / Decimal('100'))
        return cost


def _items_carrito(request):
    """
    Construye la lista de items del carrito desde la sesión con precio final y subtotales.
    Retorna: (items, subtotal_sin_desc, subtotal_con_desc)
    """
    carrito = request.session.get('carrito', {})  # dict { product_id_str: cantidad }
    product_ids = [int(pid) for pid in carrito.keys()] if carrito else []
    productos = Product.objects.filter(id__in=product_ids)

    items = []
    subtotal_sin_desc = Decimal('0')
    subtotal_con_desc = Decimal('0')

    for producto in productos:
        cantidad = int(carrito.get(str(producto.id), 0))
        if cantidad <= 0:
            continue

        precio_original = Decimal(str(producto.cost))
        precio_final = _precio_final(producto)

        subtotal_original = precio_original * cantidad
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

def agregar_al_carrito(request, product_id):
    """
    Agrega un producto al carrito en sesión.
    - Valida disponibilidad y stock.
    - Incrementa cantidad si el producto ya estaba.
    """
    carrito = request.session.get('carrito', {})
    producto = get_object_or_404(Product, id=product_id)

    if not producto.is_available or producto.stock == 0:
        messages.warning(request, "Este producto no está disponible o está agotado.")
        return redirect('store:ver_carrito')

    pid = str(product_id)
    carrito[pid] = carrito.get(pid, 0) + 1

    request.session['carrito'] = carrito
    messages.success(request, f"Se agregó {producto.name} al carrito.")
    return redirect('store:ver_carrito')


def vaciar_carrito(request):
    """Limpia el carrito de la sesión."""
    request.session['carrito'] = {}
    messages.info(request, "Tu carrito fue vaciado.")
    return redirect('store:ver_carrito')


def ver_carrito(request):
    """
    Muestra el carrito con precios y subtotales.
    Aplica descuentos en la UI del carrito.
    """
    items, subtotal_sin_desc, subtotal_con_desc = _items_carrito(request)
    descuento_total = subtotal_sin_desc - subtotal_con_desc
    iva = subtotal_con_desc * Decimal('0.19')
    total = subtotal_con_desc + iva

    context = {
        'items': items,
        'subtotal': subtotal_con_desc,
        'descuento': descuento_total,
        'iva': iva,
        'total': total,
    }
    return render(request, 'store/carrito.html', context)


# =========================
# Tienda y catálogo
# =========================
def store(request):
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

    categorias = Category.objects.all()

    context = {
        'banners': banners,
        'productos_destacados': productos_destacados,
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_actual,
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
    # 🛒 Obtener carrito y método de pago desde la sesión
    carrito = request.session.get('carrito', {})
    metodo_pago = request.session.get('metodo_pago', 'No especificado')

    # 🚫 Validar si el carrito está vacío
    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('store:checkout')

    # 🧾 Crear factura inicial con total en cero
    factura = Factura.objects.create(
        usuario=request.user,
        total=Decimal('0.00'),
        metodo_pago=metodo_pago
    )

    # 🔢 Inicializar acumuladores
    items_detalle = []
    subtotal_con_desc = Decimal('0')
    subtotal_sin_desc = Decimal('0')
    iva_total = Decimal('0')

    # 🔄 Recorrer productos del carrito
    for pid_str, cantidad in carrito.items():
        producto = get_object_or_404(Product, id=int(pid_str))
        cantidad = int(cantidad)

        precio_original = Decimal(str(producto.cost))
        precio_final = _precio_final(producto)

        subtotal_original = precio_original * cantidad
        subtotal_final = precio_final * cantidad

        # 🧾 Crear detalle de factura
        detalle = DetalleFactura.objects.create(
            factura=factura,
            producto=producto,
            cantidad=cantidad,
            subtotal=subtotal_final
        )
        items_detalle.append(detalle)

        # 📊 Acumular subtotales
        subtotal_sin_desc += subtotal_original
        subtotal_con_desc += subtotal_final

        # 🧮 Calcular IVA si aplica
        if not producto.is_tax_exempt:
            iva_total += subtotal_final * Decimal('0.19')

    # 🎯 Calcular totales finales
    descuento_total = subtotal_sin_desc - subtotal_con_desc
    total_final = subtotal_con_desc + iva_total

    # 💳 Determinar estado del pago
    estado_pago = {
        "contraentrega": "Pendiente",
        "banco": "Pagado"
    }.get(metodo_pago, "No definido")

    # 💾 Guardar totales en la factura
    factura.total = total_final
    factura.estado_pago = estado_pago
    factura.save()

    # 🧹 Limpiar carrito
    request.session['carrito'] = {}

    # 📧 Enviar factura por correo con PDF adjunto
    enviar_factura_por_correo(factura, request.user)

    # 📦 Preparar contexto para mostrar factura
    contexto = {
        "factura": factura,
        "items": items_detalle,
        "subtotal": subtotal_con_desc,
        "iva": iva_total,
        "descuento": descuento_total,
        "total_final": total_final,
        "estado_pago": estado_pago,
    }

    # 🖥️ Renderizar plantilla HTML de factura
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
        'total_final': factura.total
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

from django.shortcuts import get_object_or_404, render

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

# 🌐 Vista informativa de "Nosotros"
def nosotros(request):
    return render(request, 'store/nosotros.html')


def contacto(request):
    return render(request, 'store/contacto.html')