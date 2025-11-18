from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from home import views as home_views  # ✅ Usamos la vista home como portada

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('usuario.urls')),
    path('', home_views.home, name="inicio"),  # ✅ Portada con vitrina
    path('store/', include('store.urls')),
    path('home/', include('home.urls')),  # opcional si querés mantener /home/
    path('categorias/', include('categorias.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)