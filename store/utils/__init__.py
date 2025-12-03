from decimal import Decimal

def formatear_numero(valor) -> str:
    """
    Devuelve un número con separadores de miles estilo colombiano.
    Ejemplo: 1234567 -> '1.234.567'
    """
    try:
        valor = Decimal(str(valor))
    except Exception:
        return str(valor)
    return f"{int(valor):,}".replace(",", ".")
