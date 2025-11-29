from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def formato_numero(valor):
    return f"{valor:,.2f}".replace(",", ".").replace(".", ",", 1)

c = canvas.Canvas("factura_test.pdf", pagesize=letter)
c.setFont("Helvetica", 12)
c.drawString(100, 750, "Factura de prueba - LatinShop")
c.drawString(100, 730, "Cliente: Jairo")
c.drawString(100, 710, f"Total: ${formato_numero(356643)}")
c.save()