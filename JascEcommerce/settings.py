from pathlib import Path

# 📁 Base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Seguridad
SECRET_KEY = 'django-insecure-x&c#ax^ao22vn5@i1kjwf!7t=_8k%90d9c9y_80j_wd@2(e@dp'
DEBUG = True

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
    'jazzmin',
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 🎨 Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'JascEcommerce/static']
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
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'categorias.context_processors.menu_links',
            ],
        },
    },
]

# 🆔 Campo por defecto para claves primarias
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Library Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Library",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Library",
    "welcome_sign": "Welcome to the Library Admin",
    
    "copyright": "Jasc Ecommerce Ltd 2025",  
}

# 📁 Archivos multimedia (imágenes de productos, usuarios, etc.)
MEDIA_URL = '/media/'  # URL pública para acceder a archivos multimedia
MEDIA_ROOT = BASE_DIR / 'media'  # Carpeta local donde se guardan los archivos subidos

# 🔐 Redirecciones de autenticación
LOGIN_URL = 'login'                 # URL de inicio de sesión (name='login' en usuario/urls.py)
LOGIN_REDIRECT_URL = '/account/'    # Redirige al dashboard tras login exitoso
LOGOUT_URL = 'logout'               # URL para cerrar sesión (name='logout')
LOGOUT_REDIRECT_URL = '/home/'      # Redirige a la portada tras cerrar sesión

# 📧 Backend de correo para desarrollo (recuperación de contraseña)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Muestra correos en consola para pruebas

from datetime import datetime
STATIC_VERSION = datetime.now().strftime("%Y%m%d%H%M%S")

# 📌 Para producción, reemplaza el backend de correo por uno real:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu_correo@gmail.com'
# EMAIL_HOST_PASSWORD = 'tu_contraseña_o_token'

