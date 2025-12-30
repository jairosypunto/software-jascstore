from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Factura
from store.utils.email import enviar_correo  # ✅ usa SendGrid API

@receiver(post_save, sender=Factura)
def enviar_actualizacion_estado(sender, instance, created, **kwargs):
    """
    Envía un correo de actualización de estado SOLO si la factura cambia a
    'Pendiente' o 'Fallido'. La factura con PDF adjunto se envía aparte
    cuando el estado es 'Pagado'.
    """
    if not created and instance.email:
        # Solo enviar si el estado es relevante
        if instance.estado_pago in ["Pendiente", "Fallido"]:
            asunto = f"Actualización de tu pedido #{instance.id}"
            mensaje = (
                f"Hola {instance.nombre},\n\n"
                f"Tu pedido ahora está en estado: {instance.get_estado_pedido_display()}.\n\n"
                "Gracias por comprar en JascShop."
            )
            enviar_correo(instance.email, asunto, mensaje)
            print(f"✅ Correo de actualización enviado para pedido #{instance.id} con estado {instance.estado_pago}")
        else:
            print(f"⚠️ No se envió correo de actualización para pedido #{instance.id} porque el estado es {instance.estado_pago}")