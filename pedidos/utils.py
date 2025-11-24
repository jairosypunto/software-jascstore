def calcular_total(carrito):
    total = 0
    for item in carrito.values():
        if isinstance(item, dict) and 'precio' in item and 'cantidad' in item:
            total += item['precio'] * item['cantidad']
    return total

