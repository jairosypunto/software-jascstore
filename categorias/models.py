from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)  # ✅ Nombre de la categoría
    slug = models.SlugField(max_length=100, unique=True)  # ✅ Slug único para URL

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name  # ✅ Muestra el nombre en el panel admin y en relaciones