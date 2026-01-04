from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import store.signals

        # Crear superusuario si no existe
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="siprofesional@gamil.com",
                password="jasc2026!",
                name="Jairo",
                lastname="Salazar"
            )

        # 🔄 Re-vincular storage de los modelos al default (Cloudinary)
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
                except Exception:
                    pass