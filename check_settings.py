from django.conf import settings
print("DEBUG =", settings.DEBUG)
print("ALLOWED_HOSTS =", settings.ALLOWED_HOSTS)
print("CSRF_TRUSTED_ORIGINS =", settings.CSRF_TRUSTED_ORIGINS)
print("DATABASE =", settings.DATABASES['default'])