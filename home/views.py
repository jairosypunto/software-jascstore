from django.shortcuts import render
from store.models import Product

def home(request):
    # ✅ Solo productos destacados y disponibles
    productos = Product.objects.filter(is_available=True, destacado=True)

    # 🔍 Filtro por búsqueda (nombre y descripción)
    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(
            name__icontains=search_query
        ) | productos.filter(
            description__icontains=search_query
        )

    # 🔃 Ordenamiento
    order = request.GET.get('order')
    if order == 'name':
        productos = productos.order_by('name')
    elif order == 'price':
        productos = productos.order_by('cost')
    elif order == 'price_desc':
        productos = productos.order_by('-cost')
    elif order == 'newest':
        productos = productos.order_by('-created_at')  # 👈 si tu modelo tiene created_at

    # 📦 Contexto para el template
    context = {
        'productos_destacados': productos,
        'page_title': "JascStore - Productos destacados",  # 👈 útil para SEO dinámico
        'search_query': search_query,
        'order': order,
    }
    return render(request, 'home/home.html', context)

from django.http import HttpResponse

def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Disallow:\n\n"
        "Sitemap: https://jascstore.com/sitemap.xml"
    )
    return HttpResponse(content, content_type="text/plain")