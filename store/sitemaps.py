from django.contrib.sitemaps import Sitemap
from .models import Product

class ProductSitemap(Sitemap):
    changefreq = "daily"       # Google revisa tus productos cada día
    priority = 0.8             # Alta prioridad en el sitio
    protocol = "https"         # Fuerza HTTPS en las URLs

    def items(self):
        # Solo productos activos y disponibles
        return Product.objects.filter(is_active=True, is_available=True)

    def lastmod(self, obj):
        # Usa el campo de última actualización si existe
        return getattr(obj, "updated_at", None)