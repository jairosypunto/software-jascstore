from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Factura

@receiver(post_save, sender=Factura)
def enviar_actualizacion_estado(sender, instance, created, **kwargs):
    # Solo enviamos correo si la factura ya existía y se actualizó
    if not created:
        asunto = f"Actualización de tu pedido #{instance.id}"
        mensaje = f"Hola {instance.nombre},\n\nTu pedido ahora está en estado: {instance.get_estado_pedido_display()}.\n\nGracias por comprar en JascShop."
        
        send_mail(
            asunto,
            mensaje,
            "no-reply@jascshop.com",  # Cambia por tu correo de envío
            [instance.email],
            fail_silently=False,
        )