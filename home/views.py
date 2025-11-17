from django.shortcuts import render
from store.models import Product
from categorias.models import Category  # ✅ Import correcto desde la app 'categorias'

def home(request):
    # 🔍 Captura parámetros GET
    query = request.GET.get('q')         # Búsqueda por nombre
    order = request.GET.get('order')     # Ordenamiento
    category = request.GET.get('category')  # Filtro por categoría (slug)

    # 🛍️ Base de productos disponibles
    products = Product.objects.filter(is_available=True)

    # 🔍 Filtro por búsqueda
    if query:
        products = products.filter(name__icontains=query)

    # 🗂️ Filtro por categoría (solo si no es 'all')
    if category and category != 'all':
        products = products.filter(category__slug=category)  # ✅ Usa el nombre correcto del campo

    # 🔃 Ordenamiento
    if order == 'name':
        products = products.order_by('name')
    elif order == 'price':
        products = products.order_by('cost')

    # 📦 Carga categorías para el navbar
    categories = Category.objects.all()

    # 🧠 Contexto para el template
    context = {
        'products': products,
        'links': categories,  # Se usa en navbar.html
    }

    return render(request, "home/home.html", context)