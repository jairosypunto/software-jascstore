from django.shortcuts import render
from .models import Product
from categorias.models import Category

def store(request, category_slug=None):
    productos = Product.objects.filter(is_available=True)  # ✅ Solo productos disponibles
    categorias = Category.objects.all()

    query = request.GET.get('q')
    if query:
        productos = productos.filter(name__icontains=query)

    categoria_id = request.GET.get('categoria')
    if categoria_id and categoria_id != '0':
        productos = productos.filter(category_id=categoria_id)

    if category_slug:
        productos = productos.filter(category__slug=category_slug)

    orden = request.GET.get('orden')
    if orden == 'precio_asc':
        productos = productos.order_by('cost')
    elif orden == 'precio_desc':
        productos = productos.order_by('-cost')

    return render(request, 'store/tienda.html', {
        'productos': productos,
        'categorias': categorias,
        'section': 'store'
    })