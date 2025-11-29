from django.db import models
from django.conf import settings  # Para vincular la factura al usuario autenticado
from categorias.models import Category
from decimal import Decimal  # ✅ Para cálculos financieros precisos

# 🛍️ Modelo de Producto
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Nombre único del producto
    slug = models.SlugField(max_length=100, unique=True)  # Slug para URL amigable
    description = models.TextField()  # Descripción del producto
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # Precio base
    discount = models.PositiveIntegerField(default=0)  # Porcentaje de descuento
    image = models.ImageField(upload_to='imgs/products/', blank=True, null=True)  # Imagen opcional
    stock = models.PositiveIntegerField()  # Cantidad disponible en inventario
    is_available = models.BooleanField(default=True)  # Disponibilidad del producto
    category = models.ForeignKey('categorias.Category', on_delete=models.CASCADE)  # Relación con categoría
    destacado = models.BooleanField(default=False)  # Producto destacado
    nuevo = models.BooleanField(default=False)  # Producto nuevo
    is_tax_exempt = models.BooleanField(default=False)  # ✅ Nuevo campo: exento de IVA
    date_register = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    date_update = models.DateTimeField(auto_now=True)  # Fecha de última actualización

    def __str__(self):
        return self.name

    def final_price(self):
        """✅ Calcula el precio con descuento aplicado usando Decimal"""
        if self.discount > 0:
            descuento = Decimal(self.discount) / Decimal('100')
            return self.cost * (Decimal('1') - descuento)
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
    factura = models.ForeignKey(Factura, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad}"
    
# store/models.py

class Banner(models.Model):
    title = models.CharField(max_length=200, default="Bienvenido a LatinShop")
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to="banners/")

    def __str__(self):
        return self.title