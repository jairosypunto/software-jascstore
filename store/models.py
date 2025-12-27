from django.db import models
from django.conf import settings
from decimal import Decimal

# 🧾 Nota histórica:
# El modelo Category antes vivía en la app `categorias`.
# Ahora está consolidado en `store` para simplificar el proyecto y evitar dependencias rotas.
# El campo Product.category apunta directamente a store.Category.
from django.db import models

class Configuracion(models.Model):
    iva_activo = models.BooleanField(default=True)

    def __str__(self):
        return "Configuración general"

# 📂 Modelo de Categoría
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


# 🛍️ Modelo de Producto
class Product(models.Model):
    """Modelo principal de productos, con variantes y multimedia."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    # 💰 Precios y descuentos
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)

    # 📸 Imagen principal
    image = models.ImageField(upload_to="imgs/products/", blank=True, null=True)

    # 📦 Stock y disponibilidad
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    # 🔗 Relación con categoría
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="Categoría a la que pertenece el producto"
    )

    # ⭐ Flags de marketing
    destacado = models.BooleanField(default=False, help_text="Producto destacado en portada")
    nuevo = models.BooleanField(default=False, help_text="Producto marcado como nuevo")
    is_tax_exempt = models.BooleanField(default=False, help_text="Exento de impuestos")

    # 📅 Fechas de registro y actualización
    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # 👕 Variantes (listas separadas por comas)
    talla = models.CharField(
        max_length=200,
        blank=True,
        help_text="Lista separada por comas: S,M,L,XL"
    )
    color = models.CharField(
        max_length=200,
        blank=True,
        help_text="Lista separada por comas: Blanco,Negro,Azul"
    )

    # 🎥 Multimedia
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to="videos/products/", blank=True, null=True)
    video_thumb = models.ImageField(upload_to="imgs/products/video_thumbs/", blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def has_variants(self):
        """Devuelve True si el producto tiene tallas o colores configurados."""
        return bool(self.talla_list or self.color_list)

    @property
    def final_price(self):
        """Calcula el precio final aplicando descuento."""
        try:
            discount_value = int(self.discount)
        except (ValueError, TypeError):
            discount_value = 0

        if discount_value > 0:
            descuento = Decimal(discount_value) / Decimal('100')
            return self.cost * (Decimal('1') - descuento)
        return self.cost

    @property
    def talla_list(self):
        """Devuelve lista de tallas separadas por comas."""
        return [s.strip() for s in self.talla.split(",") if s.strip()] if self.talla else []

    @property
    def color_list(self):
        """Devuelve lista de colores separadas por comas."""
        return [c.strip() for c in self.color.split(",") if c.strip()] if self.color else []

from django.conf import settings
from django.db import models
from store.models import Product  # Ajusta el import según tu estructura

# 🧾 Modelo de Factura
class Factura(models.Model):
    """Factura generada tras una compra."""

    # 👤 Usuario que realizó la compra
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Usuario dueño de la factura"
    )

    # 📅 Fecha de creación automática
    fecha = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación de la factura"
    )

    # 💰 Total final con impuestos y descuentos
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total final con impuestos y descuentos"
    )

    # 💳 Información de pago
    metodo_pago = models.CharField(
        max_length=30,
        default="No especificado",
        help_text="Método de pago elegido"
    )
    estado_pago = models.CharField(
        max_length=20,
        default="Pendiente",
        help_text="Estado del pago"
    )
    es_pago_real = models.BooleanField(
        default=False,
        help_text="Indica si el pago fue confirmado por el proveedor o es simulado"
    )
    transaccion_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="ID de transacción del banco/proveedor"
    )
    banco = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Banco usado en el pago si aplica"
    )

    # 🚚 Datos de envío del cliente
    nombre = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Nombre completo del cliente"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Correo electrónico del cliente"
    )
    telefono = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Teléfono de contacto"
    )
    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Dirección de entrega"
    )
    ciudad = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Ciudad de entrega"
    )
    departamento = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Departamento de entrega"
    )

    # 📦 Estado del pedido
    ESTADOS_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('preparacion', 'En preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]
    estado_pedido = models.CharField(
        max_length=20,
        choices=ESTADOS_PEDIDO,
        default='pendiente',
        help_text="Estado actual del pedido"
    )

    def __str__(self):
        return f"Factura {self.id} - {self.usuario}"
    
# 📦 Modelo de DetalleFactura
class DetalleFactura(models.Model):
    """Detalle de cada producto dentro de una factura."""

    factura = models.ForeignKey(
        Factura,
        related_name="detalles",
        on_delete=models.CASCADE
    )
    producto = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # 🎽 Variantes del producto (opcional)
    talla = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    color = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    def variantes(self):
        """Devuelve un string con las variantes seleccionadas (talla y color)."""
        partes = []
        if self.talla:
            partes.append(f"Talla: {self.talla}")
        if self.color:
            partes.append(f"Color: {self.color}")
        return " | ".join(partes) if partes else "Sin variantes"

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad} ({self.variantes()})"  
    
# 📦 Modelo de DetalleFactura
class DetalleFactura(models.Model):
    """Detalle de cada producto dentro de una factura."""

    factura = models.ForeignKey(
        Factura,
        related_name="detalles",
        on_delete=models.CASCADE
    )
    producto = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # 🎽 Variantes del producto (opcional)
    talla = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    color = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    def variantes(self):
        """Devuelve un string con las variantes seleccionadas (talla y color)."""
        partes = []
        if self.talla:
            partes.append(f"Talla: {self.talla}")
        if self.color:
            partes.append(f"Color: {self.color}")
        return " | ".join(partes) if partes else "Sin variantes"

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad} ({self.variantes()})"
    
# 🎯 Modelo de Banner
class Banner(models.Model):
    """Banner principal para la tienda (portada)."""
    title = models.CharField(max_length=200, default="Bienvenido a JascShop")
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to="banners/")

    def __str__(self):
        return self.title


# 📦 Modelo de imágenes adicionales
class ProductImage(models.Model):
    """Galería de imágenes adicionales para un producto."""
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="imgs/products/gallery/")

    def __str__(self):
        return f"{self.product.name} - {self.id}"