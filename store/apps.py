from django.apps import AppConfig
from django.contrib.auth import get_user_model

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import store.signals
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="siprofesional@gamil.com",
                password="jasc2026!",
                name="Jairo",
                lastname="Salazar"
            )