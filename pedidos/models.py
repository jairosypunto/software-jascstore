from django.db import models
from django.conf import settings  # Para usar AUTH_USER_MODEL

# Modelo de Producto
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Aquí va el campo de imagen con default
    image = models.ImageField(upload_to="products/", default="products/default.jpg")

    def __str__(self):
        return self.name


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