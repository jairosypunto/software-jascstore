from django.db import models
from django.conf import settings
from categorias.models import Category
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="imgs/products/", blank=True, null=True)
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey("categorias.Category", on_delete=models.CASCADE)
    destacado = models.BooleanField(default=False)
    nuevo = models.BooleanField(default=False)
    is_tax_exempt = models.BooleanField(default=False)
    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # Variantes
    sizes = models.CharField(max_length=200, blank=True, help_text="Lista separada por comas: S,M,L,XL")
    colors = models.CharField(max_length=200, blank=True, help_text="Lista separada por comas: Blanco,Negro,Azul")

    # Video
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to="videos/products/", blank=True, null=True)
    video_thumb = models.ImageField(upload_to="imgs/products/video_thumbs/", blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if self.discount > 0:
            descuento = Decimal(str(self.discount)) / Decimal("100")
            return self.cost * (Decimal("1") - descuento)
        return self.cost

    @property
    def sizes_list(self):
        return [s.strip() for s in self.sizes.split(",")] if self.sizes else []

    @property
    def colors_list(self):
        return [c.strip() for c in self.colors.split(",")] if self.colors else []

# 🧾 Modelo de Factura
class Factura(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Usuario dueño de la factura"
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación de la factura"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total final de la factura con impuestos y descuentos"
    )
    metodo_pago = models.CharField(
        max_length=30,
        default="No especificado",
        help_text="Método de pago elegido (banco, contraentrega, etc.)"
    )
    estado_pago = models.CharField(
        max_length=20,
        default="Pendiente",
        help_text="Estado del pago (Pendiente, Pagado, Fallido)"
    )
    transaccion_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="ID de transacción del proveedor de pagos"
    )
    banco = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Banco usado en el pago si aplica"
    )

    def __str__(self):
        return f"Factura {self.id} - {self.usuario}"

# 📦 Modelo de DetalleFactura
class DetalleFactura(models.Model):
    factura = models.ForeignKey(
        Factura,
        related_name="detalles",
        on_delete=models.CASCADE,
        help_text="Factura a la que pertenece este detalle"
    )
    producto = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text="Producto comprado"
    )
    cantidad = models.PositiveIntegerField(
        help_text="Cantidad de unidades compradas"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Subtotal de esta línea (precio unitario * cantidad)"
    )
    talla = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Talla seleccionada por el cliente"
    )
    color = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Color seleccionado por el cliente"
    )

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad}"
# 🎯 Modelo de Banner
class Banner(models.Model):
    title = models.CharField(max_length=200, default="Bienvenido a JascShop")
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to="banners/")

    def __str__(self):
        return self.title

# 📦 Modelo de imágenes adicionales
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="imgs/products/gallery/")

    def __str__(self):
        return f"{self.product.name} - {self.id}"
    

