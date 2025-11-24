from django.db import models
from django.conf import settings   # Para vincular la factura al usuario autenticado
from categorias.models import Category

# 🛍️ Modelo de Producto
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)  # porcentaje de descuento
    image = models.ImageField(upload_to='imgs/products/', blank=True, null=True)
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey('categorias.Category', on_delete=models.CASCADE)
    destacado = models.BooleanField(default=False)
    nuevo = models.BooleanField(default=False)
    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def final_price(self):
        """Calcula el precio con descuento aplicado"""
        if self.discount > 0:
            return self.cost * (1 - self.discount / 100)
        return self.cost


# 🧾 Modelo de Factura
class Factura(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    metodo_pago = models.CharField(max_length=30, default="No especificado")
    estado_pago = models.CharField(max_length=20, default="Pendiente")
    transaccion_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Factura {self.id} - {self.usuario}"


# 📦 Modelo de DetalleFactura
class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name="detalles", on_delete=models.CASCADE)  # Relación con factura
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)  # Producto comprado
    cantidad = models.PositiveIntegerField()  # Cantidad
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Subtotal

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad}"
    
    from django.db import models

