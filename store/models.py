from django.db import models
from django.conf import settings
from decimal import Decimal

# 🧾 Nota histórica:
# El modelo Category antes vivía en la app `categorias`.
# Ahora está consolidado en `store` para simplificar el proyecto y evitar dependencias rotas.
# El campo Product.category apunta directamente a store.Category.


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


from django.db import models
from django.db.models import Sum
from decimal import Decimal

class Product(models.Model):
    """Modelo ÚNICO y principal de productos para JascEcommerce."""

    # Identificación
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    # Precios y descuentos
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)

    # Imagen principal
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    # Stock y disponibilidad
    # Se sincroniza automáticamente con ProductVariant
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    # Relación con categoría
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="products"
    )

    # Flags de marketing
    destacado = models.BooleanField(default=False)
    nuevo = models.BooleanField(default=False)
    is_tax_exempt = models.BooleanField(default=False)

    # Fechas
    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # Variantes (Listas para los chips del modal)
    talla = models.CharField(max_length=200, blank=True, help_text="S,M,L,XL")
    color = models.CharField(max_length=200, blank=True, help_text="Blanco,Negro,Azul")

    # Multimedia
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to="videos/products/", blank=True, null=True)
    video_thumb = models.ImageField(upload_to="video_thumbs/", blank=True, null=True)

    def __str__(self):
        return self.name

    # ================= LÓGICA DE SINCRONIZACIÓN =================

    def actualizar_stock_total(self):
        """
        Suma el stock de todas las variantes vinculadas y actualiza 
        el stock principal sin entrar en bucle infinito.
        """
        # Verificamos si existen variantes usando el related_name 'variants_stock'
        if hasattr(self, 'variants_stock'):
            total = self.variants_stock.aggregate(Sum('stock'))['stock__sum'] or 0
            # Actualizamos directamente en la base de datos para no disparar save() nuevamente
            Product.objects.filter(pk=self.pk).update(stock=total)
            self.stock = total

    def save(self, *args, **kwargs):
        """Guarda el producto y sincroniza el stock global."""
        super().save(*args, **kwargs)
        # Una vez que el producto existe (pk asignado), sincronizamos
        if self.pk:
            self.actualizar_stock_total()

    # ================= PROPIEDADES PARA EL TEMPLATE =================

    @property
    def final_price(self):
        """Calcula el precio aplicando el descuento configurado."""
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
        """Limpia el string de tallas para el Modal."""
        return [s.strip() for s in self.talla.split(",") if s.strip()] if self.talla else []

    @property
    def color_list(self):
        """Limpia el string de colores para el Modal."""
        return [c.strip() for c in self.color.split(",") if c.strip()] if self.color else []

    @property
    def has_variants(self):
        """Informa al template si debe mostrar el Modal de selección."""
        return bool(self.talla_list or self.color_list) 
    
# 🧾 Modelo de Factura
class Factura(models.Model):
    """Factura generada tras una compra."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Usuario dueño de la factura"
    )
    fecha = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación de la factura")
    total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total final con impuestos y descuentos")
    metodo_pago = models.CharField(max_length=30, default="No especificado", help_text="Método de pago elegido")
    estado_pago = models.CharField(max_length=20, default="Pendiente", help_text="Estado del pago")
    es_pago_real = models.BooleanField(default=False, help_text="Indica si el pago fue confirmado por el proveedor o es simulado")
    transaccion_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID de transacción del banco/proveedor")
    banco = models.CharField(max_length=100, blank=True, null=True, help_text="Banco usado en el pago si aplica")

    # 🚚 Datos de envío del cliente
    nombre = models.CharField(max_length=150, blank=True, null=True, help_text="Nombre completo del cliente")
    email = models.EmailField(blank=True, null=True, help_text="Correo electrónico del cliente")
    telefono = models.CharField(max_length=30, blank=True, null=True, help_text="Teléfono de contacto")
    direccion = models.CharField(max_length=255, blank=True, null=True, help_text="Dirección de entrega")
    ciudad = models.CharField(max_length=120, blank=True, null=True, help_text="Ciudad de entrega")
    departamento = models.CharField(max_length=120, blank=True, null=True, help_text="Departamento de entrega")

    ESTADOS_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('preparacion', 'En preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]
    estado_pedido = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente', help_text="Estado actual del pedido")
    correo_enviado = models.BooleanField(default=False, help_text="Indica si la factura fue enviada por correo al cliente")

    def __str__(self):
        return f"Factura {self.id} - {self.usuario}"


# 📦 Modelo de DetalleFactura (ACTUALIZADO CON PERSISTENCIA DE IMAGEN)
class DetalleFactura(models.Model):
    """Detalle de cada producto dentro de una factura."""
    factura = models.ForeignKey(Factura, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    talla = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    
    # 📸 NUEVO CAMPO: Aquí se guardará la URL de la imagen de la variante (La Lupa)
    # Esto evita que la imagen desaparezca cuando se limpie el carrito.
    imagen_url = models.URLField(max_length=500, blank=True, null=True)

    def variantes(self):
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
    image = models.ImageField(
        upload_to="banners/",   # ✅ carpeta limpia en Cloudinary
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title
    
    
# 📦 Modelo de imágenes adicionales
# store/models.py

class ProductImage(models.Model):
    """
    Galería de imágenes adicionales. 
    Aquí es donde sucede la magia para que la foto active el color.
    """
    product = models.ForeignKey(
        Product, 
        related_name="images", 
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="products/", 
        blank=True, 
        null=True
    )
    
    # --- NUEVO CAMPO ---
    # Este campo guardará el nombre del color (ej: "Negro").
    # Al ser un CharField, tú escribirás el nombre manualmente en el Admin.
    color_vinculado = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Escribe el color exacto (ej: Negro) para que esta foto lo active al hacer clic."
    )

    def __str__(self):
        # Mejoramos el nombre en el admin para que sepas qué foto tiene color
        return f"{self.product.name} - Color: {self.color_vinculado or 'General'}"
    
    
class ProductVariant(models.Model):
    """
    Control de inventario REAL por combinación de talla y color.
    """
    product = models.ForeignKey(
        Product, 
        related_name="variants_stock", 
        on_delete=models.CASCADE
    )
    talla = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible para esta combinación")

    class Meta:
        verbose_name = "Variante de Stock"
        verbose_name_plural = "Variantes de Stock"
        unique_together = ('product', 'talla', 'color') # Evita combinaciones duplicadas

    def __str__(self):
        return f"{self.product.name} | {self.talla or 'N/A'} - {self.color or 'N/A'} (Stock: {self.stock})"    