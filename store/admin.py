from django.contrib import admin, messages
from django.utils.html import format_html_join
from django.urls import path
from django.shortcuts import redirect

from .models import Product, ProductImage, Factura, DetalleFactura, Banner, Category, Configuracion
from store.utils.email import enviar_factura   # ✅ función oficial de envío

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
        'name',
        'cost',
        'discount',
        'final_price',
        'stock',
        'is_available',
        'category',
        'talla_buttons',   # ✅ tallas como botones
        'color_buttons',   # ✅ colores como botones
        'video_url',
        'video_file'
    )
    list_editable = ('discount',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_available', 'category', 'destacado', 'nuevo')
    inlines = [ProductImageInline]

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
        ("Portada de video", {
            "fields": ("video_thumb",)
        }),
        ("Fechas", {
            "fields": ("date_register", "date_update")
        }),
    )
    readonly_fields = ("final_price", "date_register", "date_update")

    # Métodos para mostrar tallas y colores como botones
    def talla_buttons(self, obj):
        if not obj.talla_list:
            return "-"
        return format_html_join(
            '',
            '<button style="margin:2px; padding:4px 8px; border-radius:4px; background:#eee; border:1px solid #ccc;">{}</button>',
            ((t,) for t in obj.talla_list)
        )
    talla_buttons.short_description = "Tallas"

    def color_buttons(self, obj):
        if not obj.color_list:
            return "-"
        return format_html_join(
            '',
            '<button style="margin:2px; padding:4px 8px; border-radius:4px; background:#eee; border:1px solid #ccc;">{}</button>',
            ((c,) for c in obj.color_list)
        )
    color_buttons.short_description = "Colores"


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
        'estado_pedido',
        'banco',
        'correo_enviado',
    )
    date_hierarchy = 'fecha'
    search_fields = (
        'usuario__username',
        'usuario__email',
        'nombre',
        'email',
        'telefono',
        'transaccion_id',
    )
    list_filter = (
        'estado_pago',
        'estado_pedido',
        'metodo_pago',
        'banco',
        'correo_enviado',
    )

    # ✅ Acción masiva para reenviar facturas seleccionadas
    actions = ["reenviar_factura"]

    def reenviar_factura(self, request, queryset):
        reenviadas = 0
        for factura in queryset:
            if factura.estado_pago == "Pagado":
                ok = enviar_factura(factura)   # ✅ usamos la función oficial
                if ok:
                    reenviadas += 1
        self.message_user(
            request,
            f"Se reenviaron {reenviadas} factura(s) correctamente.",
            level=messages.SUCCESS
        )
    reenviar_factura.short_description = "📧 Reenviar factura seleccionada"

    # ✅ Botón individual en el detalle de la factura
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:factura_id>/reenviar/',
                self.admin_site.admin_view(self.reenviar_factura_individual),
                name='store_factura_reenviar',
            ),
        ]
        return custom_urls + urls

    def reenviar_factura_individual(self, request, factura_id):
        factura = Factura.objects.get(pk=factura_id)
        if factura.estado_pago == "Pagado":
            ok = enviar_factura(factura)   # ✅ también aquí
            if ok:
                self.message_user(request, f"✅ Factura #{factura.id} reenviada correctamente.", level=messages.SUCCESS)
            else:
                self.message_user(request, f"❌ Error al reenviar factura #{factura.id}.", level=messages.ERROR)
        else:
            self.message_user(request, f"⚠️ Factura #{factura.id} no se puede reenviar porque el estado es {factura.estado_pago}.", level=messages.WARNING)
        return redirect(f"/admin/store/factura/{factura_id}/change/")

# ================================
# 📦 Detalle de factura
# ================================
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = (
        'factura',
        'producto',
        'cantidad',
        'talla',
        'color',
        'subtotal'
    )
    list_select_related = ('factura', 'producto')
    search_fields = ('producto__name', 'factura__usuario__username')
    list_filter = ('factura', 'talla', 'color')


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
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# ================================
# ⚙️ Configuración general
# ================================
@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ("iva_activo",)