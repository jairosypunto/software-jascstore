from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Cart

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'cost', 'stock', 'is_available',
        'nuevo', 'destacado', 'category',
        'date_register', 'date_update',
        'mostrar_imagen'
    )
    list_filter = ('is_available', 'nuevo', 'destacado', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('cost', 'stock', 'is_available')
    ordering = ('-date_register',)

    def mostrar_imagen(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 4px;" />', obj.image.url)
        return "Sin imagen"
    mostrar_imagen.short_description = 'Imagen'

admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)