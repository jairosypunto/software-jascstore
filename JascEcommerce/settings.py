from pathlib import Path
from datetime import datetime
from decouple import config
import os

# ================================
# 📁 BASE DEL PROYECTO
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Seguridad
SECRET_KEY = config("DJANGO_SECRET_KEY", default="cambia-esto-en-produccion")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = [
    "software-jascstore-production.up.railway.app",
    "jairos.pythonanywhere.com",
    "127.0.0.1",
    "localhost",
    "testserver",
]

CSRF_TRUSTED_ORIGINS = [
    "https://software-jascstore-production.up.railway.app",
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
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
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
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ================================
# 🖼️ MEDIA (Cloudinary)
# ================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": config("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
}

# ================================
# 🔐 LOGIN / LOGOUT
# ================================
LOGIN_URL = "account:login"
LOGIN_REDIRECT_URL = "/account/dashboard/"
LOGOUT_URL = "account:logout"
LOGOUT_REDIRECT_URL = "/home/"

# ================================
# 📧 MAIL (SendGrid API)
# ================================
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = config("SENDGRID_API_KEY", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@jascstore.com")

SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_ECHO_TO_STDOUT = True

# ================================
# 🆔 LLAVES PRIMARIAS
# ================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# 🔄 VERSIONADO DE STATIC
# ================================
STATIC_VERSION = "20251211231500"