from pathlib import Path
from datetime import datetime
import os
from decouple import config

# ================================
# 📁 BASE DEL PROYECTO
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Seguridad
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "cambia-esto-en-produccion")
DEBUG = True

ALLOWED_HOSTS = [
    "jairos.pythonanywhere.com",
    "127.0.0.1",
    "localhost",
    "testserver",
]

CSRF_TRUSTED_ORIGINS = [
    "https://jairos.pythonanywhere.com",
]

# ================================
# 🧠 MODELO DE USUARIO PERSONALIZADO
# ================================
AUTH_USER_MODEL = "auths.Auth"

# ================================
# 🗃️ BASE DE DATOS
# ================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ================================
# 🔐 VALIDACIÓN DE CONTRASEÑAS
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ================================
# 🌍 INTERNACIONALIZACIÓN
# ================================
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# ================================
# 📦 APLICACIONES INSTALADAS
# ================================
INSTALLED_APPS = [
    "usuario.apps.UsuarioConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps del proyecto
    "auths",
    "store",
    "home",
    "pedidos",

    # Extras
    "django.contrib.humanize",
    "django_extensions",

    # ✅ Cloudinary (media)
    "cloudinary",
    "cloudinary_storage",
]

# ================================
# ⚙️ MIDDLEWARE
# ================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ================================
# 🌐 URLS Y WSGI
# ================================
ROOT_URLCONF = "JascEcommerce.urls"
WSGI_APPLICATION = "JascEcommerce.wsgi.application"

# ================================
# 🧠 PLANTILLAS
# ================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "usuario" / "templates",
            BASE_DIR / "store" / "templates",
            BASE_DIR / "home" / "templates",
            BASE_DIR / "auths" / "templates",
            # ❌ eliminado: BASE_DIR / "categorias" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # ✅ menú de categorías desde store
                "store.context_processors.menu_links",
                "store.context_processors.total_items_carrito",
                "store.context_processors.static_version",
            ],
        },
    },
]

# ================================
# 🎨 ARCHIVOS ESTÁTICOS
# ================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "usuario" / "static",
    BASE_DIR / "store" / "static",
    BASE_DIR / "home" / "static",
    BASE_DIR / "auths" / "static",
    BASE_DIR / "static",  # favicon y extras globales
    # ❌ eliminado: BASE_DIR / "categorias" / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ================================
# 🖼️ MEDIA (Cloudinary)
# ================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Usar Cloudinary como almacenamiento por defecto
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Configuración de Cloudinary
CLOUDINARY = {
    "cloud_name": config("CLOUDINARY_CLOUD_NAME"),
    "api_key": config("CLOUDINARY_API_KEY"),
    "api_secret": config("CLOUDINARY_API_SECRET"),
    "secure": True,
}

# ================================
# 🔐 LOGIN / LOGOUT
# ================================
LOGIN_URL = "account:login"
LOGIN_REDIRECT_URL = "/account/dashboard/"
LOGOUT_URL = "account:logout"
LOGOUT_REDIRECT_URL = "/home/"

# ================================
# 📧 MAIL (SMTP)
# ================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_PASS", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ================================
# 🆔 LLAVES PRIMARIAS
# ================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# 🔄 VERSIONADO DE STATIC
# ================================
STATIC_VERSION = "20251211231500"