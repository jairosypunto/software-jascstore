from django.db import models
from django.conf import settings  # Para usar AUTH_USER_MODEL

# Modelo de Producto
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", default="products/default.jpg")

    # Campos nuevos
    tallas = models.CharField(max_length=200, blank=True, help_text="Ejemplo: 34,35,36,37,38,39,40")
    colores = models.CharField(max_length=200, blank=True, help_text="Ejemplo: Blanco,Negro,Azul")

    def __str__(self):
        return self.name

    # Propiedades para usar en el template
    @property
    def talla_list(self):
        if self.tallas:
            return [t.strip() for t in self.tallas.split(",")]
        return []

    @property
    def colors_list(self):
        if self.colores:
            return [c.strip() for c in self.colores.split(",")]
        return []

# Modelo de Pedido
class Order(models.Model):
    PAYMENT_METHODS = [
        ('contraentrega', 'Pago contraentrega'),
        ('transferencia', 'Transferencia bancaria'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    is_paid = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)

    # Relación con productos (muchos a muchos)
    products = models.ManyToManyField(Product, related_name="orders")

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username}"