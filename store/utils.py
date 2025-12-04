def formatear_numero(valor):
    return '{:,}'.format(valor).replace(',', '*').replace('.', ',').replace('*', '.')