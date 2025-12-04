# store/context_processors.py
from datetime import datetime

def total_items_carrito(request):
    """
    Context processor para contar items en el carrito.
    Ajusta según tu lógica real de carrito en sesión.
    """
    carrito = request.session.get("carrito", {})
    total_items = sum(item.get("cantidad", 0) for item in carrito.values())
    return {"total_items_carrito": total_items}

def static_version(request):
    """
    Context processor para versionar archivos estáticos.
    Devuelve un número de versión basado en fecha/hora.
    """
    return {
        "STATIC_VERSION": datetime.now().strftime("%Y%m%d%H%M%S")
    }