# create_superuser.py
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "JascEcommerce.settings")
django.setup()

User = get_user_model()

username = "admin"
email = "siprofesional2024@jascstore.com"
password = "jasc2026!"  # cámbiala por una clave segura

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superusuario creado con éxito.")
else:
    print("El superusuario ya existe.")