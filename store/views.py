from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from categorias.models import Category
from django.db.models import Q

# 🛒 Vista para agregar productos al carrito usando sesiones
def agregar_al_carrito(request, product_id):
    carrito = request.session.get('carrito', {})
    product_id_str = str(product_id)

    producto = get_object_or_404(Product, id=product_id)
    if not producto.is_available or producto.stock == 0:
        return redirect('store:ver_carrito')  # ❌ No agregar si está agotado

    carrito[product_id_str] = carrito.get(product_id_str, 0) + 1
    request.session['carrito'] = carrito
    return redirect('store:ver_carrito')

# 🛍️ Vista principal de la tienda con filtros y ordenamiento
def store(request):
    productos = Product.objects.filter(is_available=True)
    categoria = None

    # 🗂️ Filtro por categoría
    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        categoria = get_object_or_404(Category, slug=category_slug)
        productos = productos.filter(category=categoria)

    # 🔍 Filtro por búsqueda
    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # 🔃 Ordenamiento
    order = request.GET.get('order')
    if order == 'name':
        productos = productos.order_by('name')
    elif order == 'price':
        productos = productos.order_by('cost')
    elif order == 'price_desc':
        productos = productos.order_by('-cost')
    elif order == 'recent':
        productos = productos.order_by('-date_register')

    # 📋 Todas las categorías para el filtro
    categorias = Category.objects.all()

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria,
    }
    return render(request, 'store/store.html', context)

# 🧺 Vista para mostrar el contenido del carrito
def ver_carrito(request):
    carrito = request.session.get('carrito', {})  # dict: {'1': 2, '6': 1}
    product_ids = [int(pid) for pid in carrito.keys()] if carrito else []
    productos = Product.objects.filter(id__in=product_ids)

    # Construir lista de items con cantidades y subtotal
    items = []
    total = 0
    for producto in productos:
        qty = int(carrito.get(str(producto.id), 0))
        subtotal = (producto.cost or 0) * qty
        items.append({
            'producto': producto,
            'cantidad': qty,
            'subtotal': subtotal,
        })
        total += subtotal

    context = {
        'items': items,
        'carrito': carrito,
        'productos': productos,
        'total': total,
    }
    return render(request, 'store/carrito.html', context)

# 🗂️ Vista para productos por categoría específica
def productos_por_categoria(request, category_slug):
    categoria = get_object_or_404(Category, slug=category_slug)
    productos = Product.objects.filter(category=categoria, is_available=True)
    context = {
        'categoria': categoria,
        'productos': productos,
    }
    return render(request, 'store/productos_por_categoria.html', context)

# 🧹 Vista para vaciar el carrito
def vaciar_carrito(request):
    request.session['carrito'] = {}
    return redirect('store:ver_carrito')

# 💳 Vista temporal para checkout
def checkout(request):
    return render(request, 'store/checkout.html', {})