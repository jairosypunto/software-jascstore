from django.contrib import admin
from .models import Product, ProductImage, Factura, DetalleFactura, Banner

# ================================
# 🖼️ Configuración en línea de imágenes adicionales
# ================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage  # Modelo relacionado con Product
    extra = 1             # Muestra 1 campo vacío adicional para subir nuevas imágenes
    verbose_name = "Imagen adicional"
    verbose_name_plural = "Imágenes adicionales"

# ================================
# 🛍️ Producto principal
# ================================
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
    list_editable = ('discount',)  # ✅ Permite editar el descuento directamente en la lista
    prepopulated_fields = {'slug': ('name',)}  # ✅ Slug autogenerado desde el nombre
    search_fields = ('name',)  # ✅ Búsqueda por nombre del producto
    inlines = [ProductImageInline]  # ✅ Muestra imágenes adicionales dentro del formulario del producto

# ================================
# 🧾 Factura
# ================================
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'id',                # ID de la factura
        'usuario',           # Usuario que realizó la compra
        'fecha',             # Fecha de emisión
        'total'              # Total pagado
    )
    date_hierarchy = 'fecha'  # ✅ Permite filtrar por fechas en el panel
    search_fields = ('usuario__username',)  # ✅ Búsqueda por nombre de usuario

# ================================
# 📦 Detalle de factura
# ================================
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = (
        'factura',           # Factura asociada
        'producto',          # Producto comprado
        'cantidad',          # Cantidad adquirida
        'subtotal'           # Subtotal con descuento aplicado
    )
    list_select_related = ('factura', 'producto')  # ✅ Optimiza las consultas relacionadas

# ================================
# 🎯 Banner promocional
# ================================
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "image")  # ✅ Muestra título, subtítulo e imagen del banner