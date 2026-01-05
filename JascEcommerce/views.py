from django.shortcuts import render
from store.models import Product   # ⚠️ importa desde tu app "store", no desde JascEcommerce

def home(request):
    # Filtrar productos disponibles
    productos = Product.objects.filter(is_available=True)

    # Búsqueda por nombre
    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(name__icontains=search_query)

    # Ordenamiento
    order = request.GET.get('order')
    if order == 'name':
        productos = productos.order_by('name')
    elif order == 'price':
        productos = productos.order_by('cost')
    elif order == 'price_desc':
        productos = productos.order_by('-cost')

    # Contexto para la plantilla
    context = {
        'productos_destacados': productos,
    }
    return render(request, 'home/home.html', context)