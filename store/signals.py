from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Factura
from store.utils.email import enviar_correo  # ✅ usa SendGrid API

@receiver(post_save, sender=Factura)
def enviar_actualizacion_estado(sender, instance, created, **kwargs):
    # Solo enviamos correo si la factura ya existía y se actualizó
    if not created and instance.email:
        asunto = f"Actualización de tu pedido #{instance.id}"
        mensaje = (
            f"Hola {instance.nombre},\n\n"
            f"Tu pedido ahora está en estado: {instance.get_estado_pedido_display()}.\n\n"
            "Gracias por comprar en JascShop."
        )
        enviar_correo(instance.email, asunto, mensaje)