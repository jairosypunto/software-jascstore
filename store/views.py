from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Product, Factura, DetalleFactura
from categorias.models import Category

from decimal import Decimal

# 🛒 Agregar producto al carrito (usando sesiones)
def agregar_al_carrito(request, product_id):
    carrito = request.session.get('carrito', {})  # Recupera el carrito de la sesión
    product_id_str = str(product_id)

    producto = get_object_or_404(Product, id=product_id)
    if not producto.is_available or producto.stock == 0:
        return redirect('store:ver_carrito')

    # Incrementa cantidad si ya existe, o agrega nuevo
    carrito[product_id_str] = carrito.get(product_id_str, 0) + 1
    request.session['carrito'] = carrito
    return redirect('store:ver_carrito')


# 🛍️ Vista principal de la tienda con filtros
def store(request):
    productos = Product.objects.filter(is_available=True)
    categoria = None

    # Filtro por categoría
    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        categoria = get_object_or_404(Category, slug=category_slug)
        productos = productos.filter(category=categoria)

    # Filtro por búsqueda
    search_query = request.GET.get('q')
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

    categorias = Category.objects.all()

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria,
    }
    return render(request, 'store/store.html', context)


# 🧺 Ver contenido del carrito
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    product_ids = [int(pid) for pid in carrito.keys()] if carrito else []
    productos = Product.objects.filter(id__in=product_ids)

    items = []
    total = 0
    for producto in productos:
        qty = int(carrito.get(str(producto.id), 0))
        subtotal = producto.cost * qty
        items.append({
            'producto': producto,
            'cantidad': qty,
            'subtotal': subtotal,
        })
        total += subtotal

    context = {
        'items': items,
        'total': total,
    }
    return render(request, 'store/carrito.html', context)


# 🗂️ Productos por categoría
def productos_por_categoria(request, category_slug):
    categoria = get_object_or_404(Category, slug=category_slug)
    productos = Product.objects.filter(category=categoria, is_available=True)
    context = {
        'categoria': categoria,
        'productos': productos,
    }
    return render(request, 'store/productos_por_categoria.html', context)


# 🧹 Vaciar carrito
def vaciar_carrito(request):
    request.session['carrito'] = {}
    return redirect('store:ver_carrito')

# 💳 Confirmar pago y generar factura con validación de método
def confirmar_pago(request):
    if request.method == "POST":
        carrito = request.session.get('carrito', {})
        metodo_pago = request.POST.get('metodo_pago', 'No especificado')

        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('store:checkout')

        if metodo_pago not in ["banco", "contraentrega"]:
            messages.error(request, "Debes seleccionar un método de pago válido.")
            return redirect('store:checkout')

        # Guardar en sesión para usar en la siguiente vista
        request.session['carrito'] = carrito
        request.session['metodo_pago'] = metodo_pago

        if metodo_pago == "banco":
            return redirect('store:simular_pago_banco')
        else:
            return redirect('store:generar_factura')

    return redirect('store:checkout')

def checkout(request):
    carrito = request.session.get('carrito', {})
    product_ids = [int(pid) for pid in carrito.keys()] if carrito else []
    productos = Product.objects.filter(id__in=product_ids)

    items = []
    total = 0
    for producto in productos:
        qty = int(carrito.get(str(producto.id), 0))
        subtotal = producto.cost * qty
        items.append({
            'producto': producto,
            'cantidad': qty,
            'subtotal': subtotal,
        })
        total += subtotal

    context = {
        'items': items,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)

def generar_factura(request):
    carrito = request.session.get('carrito', {})
    metodo_pago = request.session.get('metodo_pago', 'No especificado')

    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('store:checkout')

    total = Decimal("0.00")
    items = []

    factura = Factura.objects.create(
        usuario=request.user,
        total=Decimal("0.00"),
        metodo_pago=metodo_pago
    )

    for pid, qty in carrito.items():
        producto = Product.objects.get(id=int(pid))
        subtotal = producto.cost * qty
        detalle = DetalleFactura.objects.create(
            factura=factura,
            producto=producto,
            cantidad=qty,
            subtotal=subtotal
        )
        items.append(detalle)
        total += subtotal

    iva = total * Decimal("0.19")
    descuento = Decimal("0.00")
    total_final = total + iva - descuento

    factura.total = total_final

    if metodo_pago == "contraentrega":
        estado_pago = "Pendiente"
    elif metodo_pago == "banco":
        estado_pago = "Pagado"
    else:
        estado_pago = "No definido"

    factura.estado_pago = estado_pago
    factura.save()

    request.session['carrito'] = {}

    contexto = {
        "factura": factura,
        "items": items,
        "subtotal": total,
        "iva": iva,
        "descuento": descuento,
        "total_final": total_final,
        "estado_pago": estado_pago,
    }
    return render(request, "store/factura.html", contexto)

def simular_pago_banco(request):
    if request.method == "POST":
        # Aquí podrías validar un campo de confirmación
        return redirect('store:generar_factura')
    return render(request, "store/simular_pago_banco.html")

# 📄 Páginas informativas
def nosotros(request):
    return render(request, 'store/nosotros.html')

def contacto(request):
    return render(request, 'store/contacto.html')