# store/utils/totales.py
from decimal import Decimal, ROUND_HALF_UP

COP = Decimal('1')  # para cuantizar sin centavos, si manejas COP en enteros

def calcular_totales(factura):
    subtotal_bruto = Decimal('0')
    subtotal = Decimal('0')
    ahorro_total = Decimal('0')

    for item in factura.detalles.all():
        cost = Decimal(item.producto.cost)               # precio original
        final = Decimal(item.producto.final_price)       # precio con descuento
        qty = Decimal(item.cantidad)

        subtotal_bruto += qty * cost
        subtotal += qty * final
        ahorro_total += qty * (cost - final)

    iva = (subtotal * Decimal('0.19')).quantize(COP, rounding=ROUND_HALF_UP)
    total_final = (subtotal + iva).quantize(COP, rounding=ROUND_HALF_UP)

    return {
        'subtotal_bruto': subtotal_bruto.quantize(COP),
        'subtotal': subtotal.quantize(COP),
        'iva': iva,
        'ahorro_total': ahorro_total.quantize(COP),
        'total_final': total_final,
    }