from django.db import models
from categorias.models import Category

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=50, unique=True )
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='imgs/products/') # con url cloudinary se sube a la nube
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    date_register = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name