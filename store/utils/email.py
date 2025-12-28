from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from decouple import config

# 📧 Enviar correo simple (texto plano)
def enviar_correo(destinatario, asunto, mensaje):
    """
    Envía un correo simple usando la API de SendGrid.
    - destinatario: correo del cliente
    - asunto: título del correo
    - mensaje: contenido en texto plano
    """
    sg = SendGridAPIClient(api_key=config("SENDGRID_API_KEY"))
    email = Mail(
        from_email=config("DEFAULT_FROM_EMAIL"),
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=mensaje
    )
    try:
        response = sg.send(email)
        print("✅ Correo enviado:", response.status_code)
        return response.status_code
    except Exception as e:
        print("❌ Error al enviar correo:", e)
        return None

# 🧾 Enviar factura con plantilla HTML
def enviar_factura(factura, contexto=None):
    """
    Envía un correo con la factura en formato HTML usando SendGrid API.
    - factura: instancia del modelo Factura
    - contexto: diccionario adicional para renderizar la plantilla
    """
    asunto = f"Factura #{factura.id} - JascEcommerce"
    html_content = render_to_string("emails/factura.html", {
        "usuario": factura.usuario,
        "factura": factura,
        "detalles": factura.detalles.all(),
        "fecha_local": localtime(factura.fecha),
        **(contexto or {})
    })

    message = Mail(
        from_email=config("DEFAULT_FROM_EMAIL"),
        to_emails=factura.usuario.email,
        subject=asunto,
        plain_text_content="Adjunto su factura.",
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(config("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"✅ Factura enviada con estado {response.status_code}")
        return response.status_code
    except Exception as e:
        print("❌ Error al enviar factura:", e)
        return None