from django.db import models
from django.conf import settings
from categorias.models import Category

# 🧃 Modelo de productos en LatinShop
class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # ✅ Campos visuales
    nuevo = models.BooleanField(default=False)
    destacado = models.BooleanField(default=False)

    def estado(self):
        return "Disponible" if self.is_available else "No disponible"

    def __str__(self):
        return self.name

    def miniatura(self):
        """✅ Retorna HTML de imagen miniatura para checkout"""
        if self.image:
            return f'<img src="{self.image.url}" width="60">'
        return '<img src="/static/store/img/default.jpg" width="60">'
    

# 🛒 Modelo para ítems en el carrito
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.product.cost * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def miniatura(self):
        """✅ Imagen miniatura del producto en el carrito"""
        return self.product.miniatura()