from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from home import views as home_views  # ✅ Usamos la vista home como portada

# ✅ Importar sitemap
from django.contrib.sitemaps.views import sitemap
from store.sitemaps import ProductSitemap

sitemaps = {
    "products": ProductSitemap,
}

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Usuarios y autenticación
    path("account/", include("usuario.urls")),
    path("account/", include("django.contrib.auth.urls")),  # Login/logout Django

    # Portada
    path("", home_views.home, name="inicio"),

    # Apps principales
    path("store/", include("store.urls")),
    path("pedidos/", include("pedidos.urls")),
    path("home/", include("home.urls")),  # opcional

    # ✅ SEO: sitemap y robots
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", home_views.robots_txt, name="robots_txt"),  # vista simple que devuelve el archivo
]

# ================================
# 📦 Archivos estáticos y media
# ================================
if settings.DEBUG:
    # 👉 Solo en desarrollo: servir media y estáticos desde el sistema de archivos
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 👉 En producción:
# - WhiteNoise sirve los estáticos automáticamente
# - Cloudinary sirve los media desde su CDN