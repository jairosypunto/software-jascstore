from datetime import datetime

def total_items_carrito(request):
    """
    Context processor para contar items en el carrito.
    Tolera valores tipo dict o enteros en session["carrito"].
    """
    carrito = request.session.get("carrito", {})
    # Si carrito no es dict (por algún flujo previo), normaliza
    if not isinstance(carrito, dict):
        return {"total_items_carrito": 0}

    total_items = 0
    for item in carrito.values():
        if isinstance(item, dict):
            total_items += int(item.get("cantidad", 0) or 0)
        else:
            # Si el valor es int/str numérico, súmalo directo
            try:
                total_items += int(item)
            except (TypeError, ValueError):
                total_items += 0

    return {"total_items_carrito": total_items}

def static_version(request):
    """
    Context processor para versionar archivos estáticos.
    Devuelve un número de versión basado en fecha/hora.
    """
    return {"STATIC_VERSION": datetime.now().strftime("%Y%m%d%H%M%S")}