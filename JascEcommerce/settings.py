from pathlib import Path
from decouple import config
import dj_database_url
import logging
import os

# Directorio Base
BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# 🔐 SEGURIDAD
# ================================
SECRET_KEY = config("DJANGO_SECRET_KEY", default="cambia-esto-en-produccion")

# Forzar interpretación correcta de DEBUG desde Railway
DEBUG = config("DEBUG", default="False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = [
    "jascstore.com",
    "www.jascstore.com",
    "jascstore.up.railway.app",
    "127.0.0.1",
    "localhost",
    "testserver",
]

CSRF_TRUSTED_ORIGINS = [
    "https://jascstore.com",
    "https://www.jascstore.com",
    "https://jascstore.up.railway.app",
]

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
    CSRF_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SAMESITE = "Lax"
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ================================
# 🧠 MODELO DE USUARIO PERSONALIZADO
# ================================
AUTH_USER_MODEL = "auths.Auth"

# ================================
# 🗃️ BASE DE DATOS (PostgreSQL)
# ================================
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "jascecommerce",
            "USER": "jairo",
            "PASSWORD": "TuClaveSegura",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.config(
            default=config("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True
        )
    }

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

    "auths",
    "store.apps.StoreConfig", 
    "home",
    "pedidos",

    "django.contrib.humanize",
    "django_extensions",

    # Cloudinary: Importante el orden para evitar conflictos
    "cloudinary",
    "cloudinary_storage",

    "corsheaders",
    "django.contrib.sitemaps",
]

# ================================
# ⚙️ MIDDLEWARE
# ================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Soporte para CSS Azul Hermoso
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    ADMINS = [("Admin", "admin@jascstore.com")]
    MANAGERS = ADMINS
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
        "django.middleware.common.BrokenLinkEmailsMiddleware"
    )

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
    BASE_DIR / "usuario" / "static" / "usuario",
    BASE_DIR / "store" / "static" / "store",
    BASE_DIR / "home" / "static" / "home",
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ================================
# 🖼️ MEDIA Y ALMACENAMIENTO (Moderno)
# ================================
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

if not DEBUG:
    STORAGES["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Compatibilidad con apps antiguas
if DEBUG:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Configuración Cloudinary para AVIF y Video de alta velocidad
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": config("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
}

# ================================
# 🔐 LOGIN / LOGOUT Y SESIONES
# ================================
LOGIN_URL = "account:login"
LOGIN_REDIRECT_URL = "/account/dashboard/"
LOGOUT_URL = "account:logout"
LOGOUT_REDIRECT_URL = "/home/"

SESSION_SAVE_EVERY_REQUEST = True  
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 86400  # 24 Horas de retención del cliente

# ================================
# 📧 MAIL (SendGrid)
# ================================
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = config("SENDGRID_API_KEY", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@jascstore.com")
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_ECHO_TO_STDOUT = True
EMAIL_USE_TLS = True
EMAIL_PORT = 587

# ================================
# 🆔 LLAVES PRIMARIAS Y TZ
# ================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# 🔄 VERSIONADO DE STATIC (Azul Hermoso)
# ================================
STATIC_VERSION = "20260130_v2"

# ================================
# 📊 LOGGING
# ================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# Logs de validación en arranque (No afectan el rebinding)
print(f"--- JascEcommerce Status ---")
print(f"DEBUG: {DEBUG}")
print(f"STORAGE: {DEFAULT_FILE_STORAGE}")
print(f"----------------------------")