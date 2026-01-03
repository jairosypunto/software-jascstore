from pathlib import Path
from datetime import datetime
from decouple import config
import os
import dj_database_url

# ================================
# 📁 BASE DEL PROYECTO
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Seguridad
# ================================
# 🔐 Seguridad
# ================================
SECRET_KEY = config("DJANGO_SECRET_KEY", default="cambia-esto-en-produccion")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = [
    "jascstore.com",
    "www.jascstore.com",
    "blissful-reflection-production-6a5b.up.railway.app",  # dominio Railway correcto
    "jairos.pythonanywhere.com",
    "127.0.0.1",
    "localhost",
    "testserver",
]

CSRF_TRUSTED_ORIGINS = [
    "https://jascstore.com",
    "https://www.jascstore.com",
    "https://blissful-reflection-production-6a5b.up.railway.app",
]

# Cookies y seguridad solo en producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True   # Actívalo cuando Railway muestre "Active SSL"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Cabeceras de seguridad adicionales
    X_FRAME_OPTIONS = "DENY"
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Reconocer HTTPS detrás del proxy de Railway
# Reconocer HTTPS detrás del proxy de Railway
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Cookies seguras y consistentes para dominio principal
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Asegurar que las cookies apliquen a jascstore.com y www
CSRF_COOKIE_DOMAIN = ".jascstore.com"
SESSION_COOKIE_DOMAIN = ".jascstore.com"

# Samesite compatible con flujo estándar de admin
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# Asegura que la middleware de CSRF está activa y en orden correcto
# (verifica que en MIDDLEWARE tengas esto y en este orden relativo)
# 'django.middleware.security.SecurityMiddleware',
# 'django.middleware.common.CommonMiddleware',
# 'django.middleware.csrf.CsrfViewMiddleware',
# 'django.contrib.sessions.middleware.SessionMiddleware',
# 'django.contrib.auth.middleware.AuthenticationMiddleware',

# ================================
# 🧠 MODELO DE USUARIO PERSONALIZADO
# ================================
AUTH_USER_MODEL = "auths.Auth"

# ================================
# 🗃️ BASE DE DATOS (Postgres Railway / Local)
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

    # ✅ CORS
    "corsheaders",

    # ✅ Sitemap para SEO
    "django.contrib.sitemaps",
]

# ================================
# ⚙️ MIDDLEWARE
# ================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # 👈 agregado antes de CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 🔐 Seguridad extra (solo producción)
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
    BASE_DIR / "auths" / "static" / "auths",
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
EMAIL_USE_TLS = True
EMAIL_PORT = 587

# ================================
# 🆔 LLAVES PRIMARIAS
# ================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# 🔄 VERSIONADO DE STATIC
# ================================
STATIC_VERSION = "20260101183500"

# ================================
# 📊 Logging en producción
# ================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",  # cambia a "DEBUG" si quieres más detalle
    },
}