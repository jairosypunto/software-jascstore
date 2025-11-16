from django.db import models
from categorias.models import Category

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_register = models.DateTimeField(auto_now_add=True)  # ✅ Fecha de creación
    date_update = models.DateTimeField(auto_now=True)        # ✅ Fecha de modificación

    def estado(self):
        return "Disponible" if self.is_available else "No disponible"

    def __str__(self):
        return self.name  # ✅ Solo retorna una cadena