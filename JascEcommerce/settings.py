from pathlib import Path
from datetime import datetime

# 📁 Base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Seguridad
SECRET_KEY = 'django-insecure-x&c#ax^ao22vn5@i1kjwf!7t=_8k%90d9c9y_80j_wd@2(e@dp'
DEBUG = False

ALLOWED_HOSTS = [
    'jairos.pythonanywhere.com',
    'jairosypunto.pythonanywhere.com',
    '127.0.0.1',
    'localhost',
]

CSRF_TRUSTED_ORIGINS = ['https://unsalted-kendall-unblushing.ngrok-free.dev']

# 📦 Aplicaciones instaladas
INSTALLED_APPS = [
    'usuario.apps.UsuarioConfig',
    # 'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'categorias',
    'auths',
    'store',
    'home',
    'django_extensions',
]

# ⚙️ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🌐 URLs y WSGI
ROOT_URLCONF = 'JascEcommerce.urls'
WSGI_APPLICATION = 'JascEcommerce.wsgi.application'

# 🧠 Modelo de usuario personalizado
AUTH_USER_MODEL = 'auths.Auth'

# 🗃️ Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 🔐 Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 Internacionalización
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# 🎨 Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'usuario' / 'static',
    BASE_DIR / 'store' / 'static',
    BASE_DIR / 'home' / 'static',
    BASE_DIR / 'auths' / 'static',
    BASE_DIR / 'categorias' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 🖼️ Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 🔐 Redirecciones de autenticación
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/account/'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = '/home/'

# 📧 Backend de correo para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 🎨 Configuración de Jazzmin
JAZZMIN_SETTINGS = {
    "site_title": "Library Admin",
    "site_header": "Library",
    "site_brand": "Library",
    "welcome_sign": "Welcome to the Library Admin",
    "copyright": "Jasc Ecommerce Ltd 2025",
}

# 🧠 Plantillas
# 🧠 Plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # ✅ Carpeta global para base.html y templates compartidos
            BASE_DIR / 'usuario' / 'templates',
            BASE_DIR / 'store' / 'templates',
            BASE_DIR / 'home' / 'templates',
            BASE_DIR / 'auths' / 'templates',
            BASE_DIR / 'categorias' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'categorias.context_processors.menu_links',  # ✅ Menú dinámico de categorías
                'store.context_processors.total_items_carrito',  # ✅ Total de ítems en el carrito
            ],
        },
    },
]

# 🆔 Campo por defecto para claves primarias
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 📁 Versión estática para cache busting
STATIC_VERSION = datetime.now().strftime("%Y%m%d%H%M%S")