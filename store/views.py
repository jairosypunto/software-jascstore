from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Product, Factura, DetalleFactura
from categorias.models import Category

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


# 💳 Confirmar pago y generar factura
def confirmar_pago(request):
    if request.method == "POST":
        carrito = request.session.get('carrito', {})
        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('store:checkout')

        total = 0
        # Crear factura
        factura = Factura.objects.create(usuario=request.user, total=0)

        # Crear detalles y acumular total
        for pid, qty in carrito.items():
            producto = Product.objects.get(id=int(pid))
            subtotal = producto.cost * qty
            DetalleFactura.objects.create(
                factura=factura,
                producto=producto,
                cantidad=qty,
                subtotal=subtotal
            )
            total += subtotal

        factura.total = total
        factura.save()

        # Vaciar carrito
        request.session['carrito'] = {}

        # Mostrar factura (no redirect)
        return render(request, "store/factura.html", {"factura": factura})

    return redirect('store:checkout')

    if request.method == "POST":
        carrito = request.session.get('carrito', {})
        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('store:checkout')

        total = 0
        # 🧾 Crear factura asociada al usuario
        factura = Factura.objects.create(usuario=request.user, total=0)

        # 📦 Crear detalles de factura con los productos del carrito
        for pid, qty in carrito.items():
            producto = Product.objects.get(id=int(pid))
            subtotal = producto.cost * qty
            DetalleFactura.objects.create(
                factura=factura,
                producto=producto,
                cantidad=qty,
                subtotal=subtotal
            )
            total += subtotal

        # Actualizar total de la factura
        factura.total = total
        factura.save()

        # 🧹 Vaciar carrito
        request.session['carrito'] = {}

        # ✅ Mostrar factura directamente
        return render(request, "store/factura.html", {"factura": factura})

    # Si alguien entra por GET, lo mandamos de nuevo al checkout
    return redirect('store:checkout')

# 💳 Checkout visual con resumen
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

# 📄 Páginas informativas
def nosotros(request):
    return render(request, 'store/nosotros.html')

def contacto(request):
    return render(request, 'store/contacto.html')


# 🛍️ Vista principal de la tienda con filtros y sugerencias
def store(request):
    productos = Product.objects.filter(is_available=True)
    categoria = None
    sugerencias = None

    # Filtro por categoría
    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        categoria = get_object_or_404(Category, slug=category_slug)
        productos = productos.filter(category=categoria)

    # Filtro por búsqueda
    search_query = request.GET.get('q', '').strip()
    if search_query:
        productos = productos.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

        # Si no hay resultados, buscar sugerencias por letra inicial
        if not productos.exists():
            letra = search_query[0].lower()
            if letra.isalpha():
                siguiente = chr(ord(letra) + 1) if letra != 'z' else ''
                sugerencias = Product.objects.filter(
                    Q(name__istartswith=letra) | Q(name__istartswith=siguiente),
                    is_available=True
                )[:6]
    else:
        search_query = ''

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
        'sugerencias': sugerencias,
        'categorias': categorias,
        'categoria_actual': categoria,
        'q': search_query,
    }
    return render(request, 'store/store.html', context)