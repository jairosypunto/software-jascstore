from .models import Category, ProductVariant, ProductImage
from decimal import Decimal

def menu_links(request):
    """Carga las categorías para el menú de navegación."""
    # Esta es la función que Django no encontraba y causaba el error
    categories = Category.objects.all().order_by("name")
    return {"menu_categories": categories}

def total_items_carrito(request):
    """Calcula totales y asegura que la imagen mostrada sea la del color elegido."""
    carrito_sesion = request.session.get("carrito", {})
    
    if not isinstance(carrito_sesion, dict):
        return {
            "total_items_carrito": 0, 
            "total_carrito": 0, 
            "carrito": []
        }

    total_items = 0
    total_dinero = 0
    items_procesados = []

    for key, item in carrito_sesion.items():
        if isinstance(item, dict):
            cantidad = int(item.get("cantidad", 0) or 0)
            prod_id = item.get("producto_id")
            talla = item.get("talla", "")
            color = item.get("color", "")
            precio = Decimal(str(item.get("precio", 0)))

            # 1. Sincronización con imagen por color (La Lupa)
            img_especifica = ProductImage.objects.filter(
                product_id=prod_id, 
                color_vinculado__iexact=color
            ).first()

            # Prioridad: 1. Imagen del color, 2. Imagen en sesión, 3. No-image
            imagen_final = item.get("imagen_url") or item.get("imagen")
            if img_especifica:
                imagen_final = img_especifica.image.url
            
            if not imagen_final:
                imagen_final = "/static/icons/no-image.png"

            # 2. Verificar Stock Real
            variante = ProductVariant.objects.filter(
                product_id=prod_id, 
                talla__iexact=talla, 
                color__iexact=color
            ).first()
            stock_real = variante.stock if variante else 0

            item_data = {
                'item_key': key,
                'producto_id': prod_id,
                'nombre': item.get("nombre", "Producto"),
                'precio': precio,
                'talla': talla,
                'color': color,
                'cantidad': cantidad,
                'imagen_url': imagen_final, 
                'stock_max': stock_real,
                'disponible': stock_real > 0,
                'subtotal': precio * cantidad
            }

            total_items += cantidad
            total_dinero += item_data['subtotal']
            items_procesados.append(item_data)

    return {
        "total_items_carrito": total_items,
        "total_carrito": total_dinero,
        "carrito": items_procesados
    }

def static_version(request):
    """Mantiene el versionado de archivos estáticos."""
    from django.conf import settings
    from datetime import datetime
    return {
        "STATIC_VERSION": getattr(
            settings, "STATIC_VERSION", datetime.now().strftime("%Y%m%d%H%M%S")
        )
    }