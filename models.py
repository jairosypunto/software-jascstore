from django.db import models
from django.conf import settings   # Para vincular la factura al usuario autenticado
from categorias.models import Category

# 🛍️ Modelo de Producto
class Product(models.Model):
    # Nombre único del producto
    name = models.CharField(max_length=50, unique=True)

    # Slug para URL amigables (ej: /producto/camiseta-verde/)
    slug = models.SlugField(max_length=100, unique=True)

    # Descripción larga del producto
    description = models.TextField()

    # Precio del producto
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    # Imagen del producto (se guarda en carpeta local o en Cloudinary si configuras)
    image = models.ImageField(upload_to='imgs/products/')

    # Cantidad disponible en inventario
    stock = models.PositiveIntegerField()

    # Estado de disponibilidad (True = se puede vender)
    is_available = models.BooleanField(default=True)

    # Relación con categoría (ej: Ropa, Electrónica, etc.)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # Fechas de registro y actualización automática
    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# 🧾 Modelo de Factura
class Factura(models.Model):
    # Usuario que realiza la compra (AUTH_USER_MODEL = tu modelo de usuario)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Fecha de creación de la factura
    fecha = models.DateTimeField(auto_now_add=True)

    # Total de la factura (se calcula sumando los subtotales de los detalles)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Factura {self.id} - {self.usuario}"


# 📦 Modelo de DetalleFactura
class DetalleFactura(models.Model):
    # Relación con la factura (una factura puede tener muchos detalles)
    factura = models.ForeignKey(Factura, related_name="detalles", on_delete=models.CASCADE)

    # Producto comprado
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Cantidad de ese producto
    cantidad = models.PositiveIntegerField()

    # Subtotal = cantidad * precio unitario
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad}"