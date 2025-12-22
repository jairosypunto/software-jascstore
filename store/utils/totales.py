from decimal import Decimal

def calcular_totales(factura):
    detalles = factura.detalles
    if hasattr(detalles, "all"):
        detalles = detalles.all()

    subtotal = Decimal("0")
    ahorro_total = Decimal("0")

    for detalle in detalles:
        producto = detalle.producto
        cantidad = Decimal(str(detalle.cantidad))

        cost = Decimal(str(producto.cost))
        final_price = Decimal(str(producto.final_price))

        subtotal += cost * cantidad
        ahorro_total += (cost - final_price) * cantidad

    # ✅ IVA eliminado, solo se calcula el total con descuento
    total_final = subtotal - ahorro_total

    return {
        "subtotal": subtotal,
        "ahorro_total": ahorro_total,
        "total_final": total_final,
    }