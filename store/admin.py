from django.contrib import admin
from .models import Product, ProductImage, Factura, DetalleFactura, Banner, Category

# ================================
# 🖼️ Configuración en línea de imágenes adicionales
# ================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Permite agregar una imagen adicional por defecto
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
        'talla',         # Tallas disponibles
        'color',         # Colores disponibles
        'video_url',     # Video externo
        'video_file'     # Video subido al servidor
    )
    list_editable = ('discount',)  # Permite editar el descuento directamente en la lista
    prepopulated_fields = {'slug': ('name',)}  # Slug autogenerado desde el nombre
    search_fields = ('name', 'description')    # Búsqueda por nombre y descripción
    list_filter = ('is_available', 'category', 'destacado', 'nuevo')  # Filtros útiles
    inlines = [ProductImageInline]  # Muestra imágenes adicionales en línea

    # Organización de campos en secciones del formulario
    fieldsets = (
        ("Información básica", {
            "fields": ("name", "slug", "description", "category", "image")
        }),
        ("Precio y stock", {
            "fields": ("cost", "discount", "final_price", "stock", "is_available", "is_tax_exempt")
        }),
        ("Opciones de producto", {
            "fields": ("talla", "color", "destacado", "nuevo")
        }),
        ("Video", {
            "fields": ("video_url", "video_file")
        }),
        ("Fechas", {
            "fields": ("date_register", "date_update")
        }),
    )
    readonly_fields = ("final_price", "date_register", "date_update")  # Campos calculados o automáticos

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
    date_hierarchy = 'fecha'  # Navegación por fechas
    search_fields = ('usuario__username', 'usuario__email')  # Búsqueda por usuario
    list_filter = ('estado_pago', 'metodo_pago', 'banco')  # Filtros por estado y método

# ================================
# 📦 Detalle de factura
# ================================
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = (
        'factura',
        'producto',
        'cantidad',
        'talla',     # Mostrar talla
        'color',     # Mostrar color
        'subtotal'
    )
    list_select_related = ('factura', 'producto')  # Optimiza consultas
    search_fields = ('producto__name',)  # Búsqueda por nombre de producto
    list_filter = ('factura', 'talla', 'color')  # Filtros útiles

# ================================
# 🎯 Banner promocional
# ================================
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "image")
    search_fields = ("title", "subtitle")

# ================================
# 🗂️ Categoría de productos
# ================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")  # Mostrar nombre y slug
    search_fields = ("name",)        # Búsqueda por nombre
    prepopulated_fields = {"slug": ("name",)}  # Slug autogenerado desde el nombre