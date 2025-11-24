from django.contrib import admin
from .models import Product, Factura, DetalleFactura

# 🛍️ Producto
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cost',
        'discount',
        'final_price',
        'stock',
        'is_available',
        'category'
    )
    list_editable = ('discount',)  # ✅ Editar descuento directamente en la lista
    prepopulated_fields = {'slug': ('name',)}  # ✅ Slug autogenerado desde el nombre
    search_fields = ('name',)  # ✅ Búsqueda por nombre

# 🧾 Factura
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'total')
    date_hierarchy = 'fecha'
    search_fields = ('usuario__username',)

# 📦 Detalle de factura
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura', 'producto', 'cantidad', 'subtotal')
    list_select_related = ('factura', 'producto')