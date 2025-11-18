# store/context_processors.py

def total_items_carrito(request):
    carrito = request.session.get('carrito', {})
    total_items = sum(carrito.values())
    return {'total_items_carrito': total_items}