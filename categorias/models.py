from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)  # ✅ Nombre visible de la categoría
    slug = models.SlugField(max_length=100, unique=True)  # ✅ Slug único para URLs amigables

    class Meta:
        verbose_name = "Categoría"  # ✅ Nombre singular en el panel de administración
        verbose_name_plural = "Categorías"  # ✅ Nombre plural en el panel de administración

    def __str__(self):
        return self.name  # ✅ Muestra el nombre en relaciones y en el admin