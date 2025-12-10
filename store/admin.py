from django.contrib import admin
from .models import Product, ProductImage, Factura, DetalleFactura, Banner

# ================================
# 🖼️ Configuración en línea de imágenes adicionales
# ================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = "Imagen adicional"
    verbose_name_plural = "Imágenes adicionales"

# ================================
# 🛍️ Producto principal
# ================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',          # Nombre del producto
        'cost',          # Precio original
        'discount',      # Porcentaje de descuento
        'final_price',   # Precio final calculado (con descuento)
        'stock',         # Unidades disponibles
        'is_available',  # Estado de disponibilidad
        'category',      # Categoría asignada
        'sizes',         # 🆕 Tallas disponibles
        'colors',        # 🆕 Colores disponibles
        'video_url',     # 🆕 Video externo
        'video_file'     # 🆕 Video subido al servidor
    )
    list_editable = ('discount',)  # ✅ Editar descuento directamente en la lista
    prepopulated_fields = {'slug': ('name',)}  # ✅ Slug autogenerado desde el nombre
    search_fields = ('name', 'description')    # ✅ Búsqueda por nombre y descripción
    list_filter = ('is_available', 'category', 'destacado', 'nuevo')  # ✅ Filtros útiles
    inlines = [ProductImageInline]

    # ✅ Organización de campos en secciones
    fieldsets = (
        ("Información básica", {
            "fields": ("name", "slug", "description", "category", "image")
        }),
        ("Precio y stock", {
            "fields": ("cost", "discount", "final_price", "stock", "is_available", "is_tax_exempt")
        }),
        ("Opciones de producto", {
            "fields": ("sizes", "colors", "destacado", "nuevo")
        }),
        ("Video", {
            "fields": ("video_url", "video_file")
        }),
        ("Fechas", {
            "fields": ("date_register", "date_update")
        }),
    )
    readonly_fields = ("final_price", "date_register", "date_update")
# ================================
# 🧾 Factura
# ================================
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'fecha',
        'total',
        'metodo_pago',
        'estado_pago',
        'banco'
    )
    date_hierarchy = 'fecha'
    search_fields = ('usuario__username', 'usuario__email')
    list_filter = ('estado_pago', 'metodo_pago', 'banco')

# ================================
# 📦 Detalle de factura
# ================================
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = (
        'factura',
        'producto',
        'cantidad',
        'subtotal'
    )
    list_select_related = ('factura', 'producto')
    search_fields = ('producto__name',)
    list_filter = ('factura',)

# ================================
# 🎯 Banner promocional
# ================================
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "image")
    search_fields = ("title", "subtitle")