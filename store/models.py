from django.db import models
from categorias.models import Category
from django.conf import settings  # ✅ Para vincular carrito al modelo de usuario configurado

# 🧃 Modelo de productos en LatinShop
class Product(models.Model):
    name = models.CharField(max_length=100)  # ✅ Nombre del producto
    slug = models.SlugField(max_length=100, unique=True)  # ✅ URL amigable única
    description = models.TextField(blank=True)  # ✅ Descripción opcional
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ Precio con decimales
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # ✅ Imagen del producto
    stock = models.PositiveIntegerField(default=0)  # ✅ Cantidad disponible
    is_available = models.BooleanField(default=True)  # ✅ Estado de disponibilidad
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # ✅ Relación con categoría
    date_register = models.DateTimeField(auto_now_add=True)  # ✅ Fecha de creación
    date_update = models.DateTimeField(auto_now=True)        # ✅ Fecha de última modificación

    # ✅ Campo visual adicional para destacar productos nuevos
    nuevo = models.BooleanField(default=False)  # ✅ Marca si el producto es nuevo
    destacado = models.BooleanField(default=False)  # ✅ Marca si el producto es destacado

    def estado(self):
        """✅ Retorna el estado legible del producto"""
        return "Disponible" if self.is_available else "No disponible"

    def __str__(self):
        """✅ Representación legible en el panel de administración"""
        return self.name

# 🛒 Modelo para carrito de compras (opcional si no usas sesiones)
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # ✅ Producto en el carrito
    quantity = models.PositiveIntegerField(default=1)  # ✅ Cantidad agregada
    added_at = models.DateTimeField(auto_now_add=True)  # ✅ Fecha de agregado

    # ✅ Usuario vinculado al carrito (usando el modelo configurado en settings)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def subtotal(self):
        """✅ Calcula el subtotal por producto"""
        return self.product.cost * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"