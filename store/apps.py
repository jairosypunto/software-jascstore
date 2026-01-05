from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import store.signals

        # ⚠️ Crear superusuario automáticamente puede dar warnings en Railway
        # Mejor hacerlo con un management command o manualmente.
        # Si decides mantenerlo aquí, al menos captura excepciones.
        try:
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    username="admin",
                    email="siprofesional@gamil.com",
                    password="jasc2026!",
                    name="Jairo",
                    lastname="Salazar"
                )
                logger.info("Superusuario 'admin' creado automáticamente.")
        except Exception as e:
            logger.error(f"Error creando superusuario: {e}")

        # 🔄 Re-vincular storage de los modelos al default (Cloudinary o FS)
        try:
            from .models import Product, Banner, ProductImage
            targets = {
                Product: ['image', 'video_file', 'video_thumb'],
                Banner: ['image'],
                ProductImage: ['image'],
            }

            for model, fields in targets.items():
                for fname in fields:
                    try:
                        field = model._meta.get_field(fname)
                        field.storage = default_storage
                        logger.info(
                            f"{model.__name__}.{fname} storage rebind → {field.storage.__class__.__name__}"
                        )
                    except Exception as e:
                        logger.error(f"Error rebinding {model.__name__}.{fname}: {e}")
        except Exception as e:
            logger.error(f"Error importando modelos en StoreConfig.ready(): {e}")
            