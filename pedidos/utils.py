def calcular_total(carrito):
    total = 0
    for item in carrito.values():
        if isinstance(item, dict):
            cantidad = int(item.get('cantidad', 0) or 0)
            precio = item.get('precio')
            if precio is None and 'producto_id' in item:
                from store.models import Product
                producto = Product.objects.filter(id=item['producto_id']).first()
                if producto:
                    precio = producto.final_price
            if precio:
                total += precio * cantidad
    return total