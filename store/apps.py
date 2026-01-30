from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # 1. Importamos las señales (Obligatorio para que el stock funcione)
        import store.signals 

        # 2. Lógica de Superusuario (Solo si realmente no existe)
        # Usamos una importación local para evitar el RuntimeWarning de la base de datos
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Verificamos la existencia del admin de forma segura
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    username="admin",
                    email="siprofesional@gamil.com",
                    password="jasc2026!",
                    name="Jairo",
                    lastname="Salazar"
                )
                logger.info("✅ Superusuario 'admin' creado exitosamente.")
        except Exception as e:
            # Esto evita que el servidor se caiga si la DB no está lista en Railway
            logger.debug(f"Nota: No se procesó el superusuario en este inicio: {e}")

        # LOG DE ÉXITO (Estilo JascEcommerce)
        print("--- Aplicación Store: Operativa y Vinculada ---")