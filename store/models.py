from django.db import models
from django.conf import settings   # Para vincular la factura al usuario autenticado
from categorias.models import Category

# 🛍️ Modelo de Producto
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='imgs/products/')
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    destacado = models.BooleanField(default=False)  # ✅ Para el home
    nuevo = models.BooleanField(default=False)      # ✅ Para marcar como nuevo
    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# 🧾 Modelo de Factura
class Factura(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # Usuario que compra
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    total = models.DecimalField(max_digits=10, decimal_places=2) # Total de la factura

    def __str__(self):
        return f"Factura {self.id} - {self.usuario}"


# 📦 Modelo de DetalleFactura
class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name="detalles", on_delete=models.CASCADE) # Relación con factura
    producto = models.ForeignKey(Product, on_delete=models.CASCADE) # Producto comprado
    cantidad = models.PositiveIntegerField() # Cantidad
    subtotal = models.DecimalField(max_digits=10, decimal_places=2) # Subtotal

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad}"