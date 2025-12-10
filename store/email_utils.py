from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def enviar_factura_por_correo(factura, pdf_path=None):
    """
    Envía un correo al usuario con los detalles de la factura.
    Si se pasa pdf_path, adjunta el PDF.
    """
    asunto = f"Factura #{factura.id} - JascEcommerce"
    mensaje = render_to_string('emails/factura.html', {
        'usuario': factura.usuario,
        'factura': factura,
        'detalles': factura.detalles.all(),
    })

    email = EmailMessage(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [factura.usuario.email]
    )
    email.content_subtype = 'html'

    if pdf_path:
        email.attach_file(pdf_path)

    email.send()