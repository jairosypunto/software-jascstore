def total_items_carrito(request):
    carrito = request.session.get('carrito', {})
    total_items = 0
    for item in carrito.values():
        if isinstance(item, dict):
            total_items += item.get('cantidad', 0)
        else:
            # Manejo seguro si todavía hay enteros viejos en la sesión
            total_items += int(item)
    return {'total_items': total_items}