from django.db import models
from django.conf import settings  # Para usar AUTH_USER_MODEL

from django.db import models
from django.contrib.auth.models import User
# ✅ IMPORTACIÓN CRÍTICA: Traemos el producto desde la única fuente de verdad
from store.models import Product 

class Order(models.Model):
    """Modelo para gestionar los pedidos realizados por los usuarios."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pendiente')
    
    # ✅ REFERENCIA CORRECTA: Ahora Product ya está definido arriba
    products = models.ManyToManyField(Product, related_name="orders")

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username}"
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
    
    