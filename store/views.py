from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Factura, DetalleFactura
from categorias.models import Category
from django.contrib.auth.decorators import login_required



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
        cost = Decimal(producto.cost)
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

        precio_original = Decimal(producto.cost)
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
    """
    Listado de productos:
    - Productos destacados (con imagen válida)
    - Filtros: categoría, búsqueda
    - Ordenamiento: nombre, precio, precio desc, reciente
    """

    # Productos destacados para carrusel
    productos_destacados = Product.objects.filter(
        destacado=True,
        is_available=True
    ).exclude(image__isnull=True).exclude(image='')[:10]

    # Base de consulta principal
    productos = Product.objects.filter(is_available=True)
    categoria_actual = None

    # Filtro por categoría
    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        categoria_actual = get_object_or_404(Category, slug=category_slug)
        productos = productos.filter(category=categoria_actual)

    # Filtro por búsqueda (validación extra para evitar errores con espacios o símbolos)
    search_query = request.GET.get('q', '').strip()
    if search_query:
        productos = productos.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Ordenamiento
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


@login_required(login_url='/accounts/login/')
def generar_factura(request):
    carrito = request.session.get('carrito', {})
    metodo_pago = request.session.get('metodo_pago', 'No especificado')

    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('store:checkout')

    factura = Factura.objects.create(
        usuario=request.user,
        total=Decimal('0.00'),
        metodo_pago=metodo_pago
    )

    items_detalle = []
    subtotal_con_desc = Decimal('0')
    subtotal_sin_desc = Decimal('0')

    for pid_str, cantidad in carrito.items():
        producto = get_object_or_404(Product, id=int(pid_str))
        cantidad = int(cantidad)

        precio_original = Decimal(producto.cost)
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

    descuento_total = subtotal_sin_desc - subtotal_con_desc
    iva = subtotal_con_desc * Decimal('0.19')
    total_final = subtotal_con_desc + iva

    estado_pago = {
        "contraentrega": "Pendiente",
        "banco": "Pagado"
    }.get(metodo_pago, "No definido")

    factura.total = total_final
    factura.estado_pago = estado_pago
    factura.save()

    request.session['carrito'] = {}

    contexto = {
        "factura": factura,
        "items": items_detalle,
        "subtotal": subtotal_con_desc,
        "iva": iva,
        "descuento": descuento_total,
        "total_final": total_final,
        "estado_pago": estado_pago,
    }
    return render(request, "store/factura.html", contexto)
    carrito = request.session.get('carrito', {})
    metodo_pago = request.session.get('metodo_pago', 'No especificado')

    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('store:checkout')

    # Creamos la factura con total temporal
    factura = Factura.objects.create(
        usuario=request.user,  # ahora siempre será un usuario válido
        total=Decimal('0.00'),
        metodo_pago=metodo_pago
    )

    items_detalle = []
    subtotal_con_desc = Decimal('0')
    subtotal_sin_desc = Decimal('0')

    for pid_str, cantidad in carrito.items():
        producto = get_object_or_404(Product, id=int(pid_str))
        cantidad = int(cantidad)

        precio_original = Decimal(producto.cost)
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

    descuento_total = subtotal_sin_desc - subtotal_con_desc
    iva = subtotal_con_desc * Decimal('0.19')
    total_final = subtotal_con_desc + iva

    if metodo_pago == "contraentrega":
        estado_pago = "Pendiente"
    elif metodo_pago == "banco":
        estado_pago = "Pagado"
    else:
        estado_pago = "No definido"

    factura.total = total_final
    factura.estado_pago = estado_pago
    factura.save()

    request.session['carrito'] = {}

    contexto = {
        "factura": factura,
        "items": items_detalle,
        "subtotal": subtotal_con_desc,
        "iva": iva,
        "descuento": descuento_total,
        "total_final": total_final,
        "estado_pago": estado_pago,
    }
    return render(request, "store/factura.html", contexto)


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


def nosotros(request):
    return render(request, 'store/nosotros.html')


def contacto(request):
    return render(request, 'store/contacto.html')