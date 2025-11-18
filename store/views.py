from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from categorias.models import Category
from django.db.models import Q

# 🛒 Agregar producto al carrito (sesiones)
def agregar_al_carrito(request, product_id):
    carrito = request.session.get('carrito', {})
    product_id_str = str(product_id)

    producto = get_object_or_404(Product, id=product_id)
    if not producto.is_available or producto.stock == 0:
        return redirect('store:ver_carrito')

    carrito[product_id_str] = carrito.get(product_id_str, 0) + 1
    request.session['carrito'] = carrito
    return redirect('store:ver_carrito')


# 🛍️ Vista principal de la tienda con filtros
def store(request):
    productos = Product.objects.filter(is_available=True)
    categoria = None

    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'all':
        categoria = get_object_or_404(Category, slug=category_slug)
        productos = productos.filter(category=categoria)

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

def nosotros(request):
    return render(request, 'store/nosotros.html')

def contacto(request):
    return render(request, 'store/contacto.html')