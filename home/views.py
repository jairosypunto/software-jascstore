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

# 🔧 Vista de depuración para configuración de almacenamiento

from django.conf import settings
from django.http import JsonResponse

def debug_storage(request):
    return JsonResponse({
        "DEBUG": settings.DEBUG,
        "DEFAULT_FILE_STORAGE": settings.DEFAULT_FILE_STORAGE,
        "CLOUDINARY_STORAGE": settings.CLOUDINARY_STORAGE,
    })
    
# Otra vista de depuración para inspeccionar campos de modelo y su almacenamiento    
    
from django.http import JsonResponse
from django.apps import apps

def debug_fields_storage(request):
    data = {}

    # Lista de modelos y campos a inspeccionar
    targets = [
        ("store", "Banner", "image"),
        ("store", "ProductImage", "image"),
        ("store", "Product", "video_thumb"),
        ("store", "Product", "image"),  # si tu Product tiene imagen principal
    ]

    for app_label, model_name, field_name in targets:
        try:
            Model = apps.get_model(app_label, model_name)
            field = Model._meta.get_field(field_name)
            data[f"{model_name}.{field_name}"] = {
                "field_class": field.__class__.__name__,
                "storage_class": field.storage.__class__.__name__,
                "upload_to": getattr(field, "upload_to", None),
            }
        except Exception as e:
            data[f"{model_name}.{field_name}"] = {"error": str(e)}

    return JsonResponse(data)

