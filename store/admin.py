from django.contrib import admin
from .models import Product  # ✅ Importación correcta desde la app store

# ✅ Configuración avanzada del panel de administración
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'cost', 'stock', 'is_available',
        'category', 'date_register', 'date_update'
    )  # ✅ Muestra columnas clave en la lista
    list_filter = ('is_available', 'category')  # ✅ Filtros laterales
    search_fields = ('name', 'description')     # ✅ Búsqueda por nombre y descripción
    prepopulated_fields = {'slug': ('name',)}   # ✅ Slug autogenerado desde el nombre
    list_editable = ('cost', 'stock', 'is_available')  # ✅ Edición directa en la lista
    ordering = ('-date_register',)  # ✅ Orden descendente por fecha de registro

# ✅ Registro del modelo con su configuración personalizada
admin.site.register(Product, ProductAdmin)