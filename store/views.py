from django.shortcuts import render, get_object_or_404
from store.models import Product
from categorias.models import Category
from django.db.models import Q

def store(request):
    productos = Product.objects.filter(is_available=True)

    # ✅ Filtro por categoría (slug desde GET)
    category_slug = request.GET.get('category')
    if category_slug:
        categoria = get_object_or_404(Category, slug=category_slug)
        productos = productos.filter(category=categoria)

    # ✅ Filtro por búsqueda
    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # ✅ Ordenamiento
    order = request.GET.get('order')
    if order == 'precio_asc':
        productos = productos.order_by('cost')
    elif order == 'precio_desc':
        productos = productos.order_by('-cost')
    elif order == 'nombre':
        productos = productos.order_by('name')
    elif order == 'reciente':
        productos = productos.order_by('-date_register')

    categorias = Category.objects.all()

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria if category_slug else None,
    }
    return render(request, 'store/tienda.html', context)