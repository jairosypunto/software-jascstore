from django.contrib import admin
from .models import Product, Factura, DetalleFactura

# 🛍️ Producto
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',              # Nombre del producto
        'cost',              # Precio original
        'discount',          # Porcentaje de descuento
        'final_price',       # Precio final calculado (con descuento)
        'stock',             # Unidades disponibles
        'is_available',      # Estado de disponibilidad
        'category'           # Categoría asignada
    )
    list_editable = ('discount',)  # ✅ Editar descuento directamente en la lista
    prepopulated_fields = {'slug': ('name',)}  # ✅ Slug autogenerado desde el nombre
    search_fields = ('name',)  # ✅ Búsqueda por nombre

# 🧾 Factura
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'id',                # ID de la factura
        'usuario',           # Usuario que realizó la compra
        'fecha',             # Fecha de emisión
        'total'              # Total pagado
    )
    date_hierarchy = 'fecha'  # ✅ Navegación por fechas
    search_fields = ('usuario__username',)  # ✅ Búsqueda por nombre de usuario

# 📦 Detalle de factura
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = (
        'factura',           # Factura asociada
        'producto',          # Producto comprado
        'cantidad',          # Cantidad adquirida
        'subtotal'           # Subtotal con descuento aplicado
    )
    list_select_related = ('factura', 'producto')  # ✅ Optimiza consultas relacionadas

from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "image")