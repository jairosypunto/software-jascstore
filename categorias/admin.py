from django.contrib import admin
from .models import Category

# ✅ Configuración del panel de administración para categorías
@admin.register(Category)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')  # ✅ Campos que sí existen en el modelo
    prepopulated_fields = {'slug': ('name',)}  # ✅ Autocompletar slug desde name
    search_fields = ('name',)  # ✅ Búsqueda por nombre
    list_filter = ('name',)    # ✅ Filtro lateral por nombre
    list_per_page = 10         # ✅ Paginación