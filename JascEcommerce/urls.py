
from django.contrib import admin
from django.urls import include, path

from JascEcommerce import settings
from .import views
from django.conf.urls.static import static #para imagenes

urlpatterns = [
path('admin/', admin.site.urls),                      # Panel de administración
path('account/', include('usuario.urls')),            # Rutas para la app de usuario
path('', views.inicio, name="inicio"),                # Vista principal (index.html)
path('store/', include('store.urls')),                # Vista de tienda
path('home/', include('home.urls')),  # ✅ Ya no compite con la raíz
path('categorias/', include('categorias.urls')),
] + static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT) #para imagenes
