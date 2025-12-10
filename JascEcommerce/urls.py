from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from home import views as home_views  # ✅ Usamos la vista home como portada

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Usuarios y autenticación
    path('account/', include('usuario.urls')),          # App personalizada
    path("accounts/", include("django.contrib.auth.urls")),  # Login/logout Django

    # Portada
    path('', home_views.home, name="inicio"),

    # Apps principales
    path('store/', include('store.urls')),
    path('categorias/', include('categorias.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('home/', include('home.urls')),  # opcional
]

# Archivos estáticos y media (solo en desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)