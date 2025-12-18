from datetime import datetime
from django.conf import settings
from .models import Category

def menu_links(request):
    """
    Context processor para inyectar categorías en el menú de navegación.
    Obtiene todas las categorías ordenadas alfabéticamente.
    """
    categories = Category.objects.all().order_by("name")
    return {"menu_categories": categories}

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
    Devuelve un número de versión fijo desde settings o dinámico por fecha/hora.
    """
    return {
        "STATIC_VERSION": getattr(
            settings, "STATIC_VERSION", datetime.now().strftime("%Y%m%d%H%M%S")
        )
    }