from pathlib import Path
from decouple import config
import dj_database_url
import logging

BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# 🔐 Seguridad
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
# 🧠 Modelo de usuario personalizado
# ================================
AUTH_USER_MODEL = "auths.Auth"

# ================================
# 🗃️ Base de datos
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
# 🔐 Validación de contraseñas
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ================================
# 🌍 Internacionalización
# ================================
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# ================================
# 📦 Aplicaciones instaladas
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
    "store.apps.StoreConfig",   # ⚠️ importante que sea StoreConfig
    "home",
    "pedidos",

    "django.contrib.humanize",
    "django_extensions",

    "cloudinary",
    "cloudinary_storage",

    "corsheaders",
    "django.contrib.sitemaps",
]

# ================================
# ⚙️ Middleware
# ================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
# 🌐 URLs y WSGI
# ================================
ROOT_URLCONF = "JascEcommerce.urls"
WSGI_APPLICATION = "JascEcommerce.wsgi.application"

# ================================
# 🧠 Plantillas
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
# 🎨 Archivos estáticos
# ================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "usuario" / "static" / "usuario",
    BASE_DIR / "store" / "static" / "store",
    BASE_DIR / "home" / "static" / "home",
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ================================
# 🖼️ Media (Local vs Cloudinary)
# ================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if DEBUG:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": config("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
}

# ================================
# 🔄 Forzar default_storage en producción
# ================================
if not DEBUG:
    try:
        from cloudinary_storage.storage import MediaCloudinaryStorage
        from django.core.files.storage import storages
        storages["default"] = MediaCloudinaryStorage()
        print("✅ default_storage forzado a MediaCloudinaryStorage en producción")
    except Exception as e:
        print("⚠️ Error configurando Cloudinary como default_storage:", e)

# ================================
# 🔐 Login / Logout
# ================================
LOGIN_URL = "account:login"
LOGIN_REDIRECT_URL = "/account/dashboard/"
LOGOUT_URL = "account:logout"
LOGOUT_REDIRECT_URL = "/home/"

# Obliga a Django a guardar el carrito en cada movimiento
SESSION_SAVE_EVERY_REQUEST = True  
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 86400  # Mantiene la sesión activa por 24 horas

# ================================
# 📧 Mail (SendGrid API)
# ================================
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = config("SENDGRID_API_KEY", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@jascstore.com")
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_ECHO_TO_STDOUT = True
EMAIL_USE_TLS = True
EMAIL_PORT = 587

# ================================
# 🆔 Llaves primarias
# ================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# 🔄 Versionado de static
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
        "level": "INFO",
    },
}

# ✅ Logging para validar en runtime
logger = logging.getLogger(__name__)
logger.info("CSRF_TRUSTED_ORIGINS = %s", CSRF_TRUSTED_ORIGINS)
logger.info("ALLOWED_HOSTS = %s", ALLOWED_HOSTS)
logger.info("DEBUG = %s", DEBUG)
logger.info("DEFAULT_FILE_STORAGE = %s", DEFAULT_FILE_STORAGE)
logger.info("CLOUDINARY_STORAGE = %s", CLOUDINARY_STORAGE)

# ✅ Debug directo en Railway
print("DEBUG =", DEBUG)
print("DEFAULT_FILE_STORAGE =", DEFAULT_FILE_STORAGE)
print("CLOUDINARY_STORAGE =", CLOUDINARY_STORAGE)

from django.core.files.storage import default_storage
print("default_storage backend class =", default_storage.__class__.__name__)