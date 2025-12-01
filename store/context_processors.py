def total_items_carrito(request):
    carrito = request.session.get('carrito', {})
    total_items = sum(int(cantidad) for cantidad in carrito.values())
    return {'total_items': total_items}

# store/context_processors.py

from django.conf import settings

def static_version(request):
    return {'STATIC_VERSION': settings.STATIC_VERSION}