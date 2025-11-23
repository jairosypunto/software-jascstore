def total_items_carrito(request):
    carrito = request.session.get('carrito', {})
    total_items = sum(int(cantidad) for cantidad in carrito.values())
    return {'total_items': total_items}