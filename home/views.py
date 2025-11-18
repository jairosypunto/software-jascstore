from django.shortcuts import render
from store.models import Product

def home(request):
    productos = Product.objects.filter(is_available=True)

    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(name__icontains=search_query)

    order = request.GET.get('order')
    if order == 'name':
        productos = productos.order_by('name')
    elif order == 'price':
        productos = productos.order_by('cost')
    elif order == 'price_desc':
        productos = productos.order_by('-cost')

    context = {
        'productos_destacados': productos,  # 👈 Este nombre debe coincidir con el template
    }
    return render(request, 'home/home.html', context)
    
    productos = Product.objects.filter(is_available=True, destacado=True)

    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(name__icontains=search_query)

    order = request.GET.get('order')
    if order == 'name':
        productos = productos.order_by('name')
    elif order == 'price':
        productos = productos.order_by('cost')
    elif order == 'price_desc':
        productos = productos.order_by('-cost')

    context = {
        'productos_destacados': productos,
    }
    return render(request, 'home/home.html', context)
    productos = Product.objects.filter(is_available=True, destacado=True)

    # 🔍 Filtro por búsqueda
    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(name__icontains=search_query)

    # 🔃 Ordenamiento
    order = request.GET.get('order')
    if order == 'name':
        productos = productos.order_by('name')
    elif order == 'price':
        productos = productos.order_by('cost')
    elif order == 'price_desc':
        productos = productos.order_by('-cost')

    context = {
        'productos_destacados': productos,
    }
    return render(request, 'home/home.html', context)