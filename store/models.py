from django.db import models
from django.conf import settings
from django.db.models import Sum, F
from decimal import Decimal

# ------------------------------------------------------------------
# CONFIGURACIÓN Y CATEGORÍAS
# ------------------------------------------------------------------

class Configuracion(models.Model):
    iva_activo = models.BooleanField(default=True)

    def __str__(self):
        return "Configuración general"

class Category(models.Model):
    """Clasificación principal de productos en la tienda."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name

# ------------------------------------------------------------------
# PRODUCTO PRINCIPAL
# ------------------------------------------------------------------

class Product(models.Model):
    """Modelo ÚNICO y principal de productos para JascEcommerce."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="products"
    )

    destacado = models.BooleanField(default=False)
    nuevo = models.BooleanField(default=False)
    is_tax_exempt = models.BooleanField(default=False)

    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    talla = models.CharField(max_length=200, blank=True, help_text="S,M,L,XL")
    color = models.CharField(max_length=200, blank=True, help_text="Blanco,Negro,Azul")

    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to="videos/products/", blank=True, null=True)
    video_thumb = models.ImageField(upload_to="video_thumbs/", blank=True, null=True)

    def __str__(self):
        return self.name

    def actualizar_stock_total(self):
        if self.pk:
            total = self.variants_stock.aggregate(Sum('stock'))['stock__sum'] or 0
            Product.objects.filter(pk=self.pk).update(stock=total)
            self.stock = total

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk:
            self.actualizar_stock_total()

    @property
    def final_price(self):
        try:
            discount_value = Decimal(self.discount)
        except (ValueError, TypeError):
            discount_value = Decimal(0)

        if discount_value > 0:
            factor = Decimal(1) - (discount_value / Decimal(100))
            return self.cost * factor
        return self.cost

    @property
    def talla_list(self):
        return [s.strip() for s in self.talla.split(",") if s.strip()] if self.talla else []

    @property
    def color_list(self):
        return [c.strip() for c in self.color.split(",") if c.strip()] if self.color else []

    @property
    def has_variants(self):
        return bool(self.talla_list or self.color_list)

# ------------------------------------------------------------------
# FACTURACIÓN
# ------------------------------------------------------------------

class Factura(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=30, default="No especificado")
    estado_pago = models.CharField(max_length=20, default="Pendiente")
    es_pago_real = models.BooleanField(default=False)
    transaccion_id = models.CharField(max_length=100, blank=True, null=True)
    banco = models.CharField(max_length=100, blank=True, null=True)

    nombre = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=120, blank=True, null=True)
    departamento = models.CharField(max_length=120, blank=True, null=True)

    ESTADOS_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('preparacion', 'En preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]
    estado_pedido = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente')
    correo_enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"Factura {self.id} - {self.usuario}"

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    talla = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    
    # Campo que faltaba en Railway
    imagen_url = models.URLField(max_length=500, blank=True, null=True)

    def variantes(self):
        partes = []
        if self.talla: partes.append(f"Talla: {self.talla}")
        if self.color: partes.append(f"Color: {self.color}")
        return " | ".join(partes) if partes else "Sin variantes"

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad}"

# ------------------------------------------------------------------
# MULTIMEDIA ADICIONAL Y VARIANTES
# ------------------------------------------------------------------

class Banner(models.Model):
    title = models.CharField(max_length=200, default="Bienvenido a JascShop")
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to="banners/", blank=True, null=True)

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    color_vinculado = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.color_vinculado or 'General'}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants_stock", on_delete=models.CASCADE)
    talla = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Variante de Stock"
        verbose_name_plural = "Variantes de Stock"
        unique_together = ('product', 'talla', 'color')

    def __str__(self):
        return f"{self.product.name} | {self.talla or 'N/A'} - {self.color or 'N/A'}"