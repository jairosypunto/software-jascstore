from django.contrib import admin, messages
from django.utils.html import format_html, format_html_join
from django.urls import path
from django.shortcuts import redirect
from django.db import models

from .models import (
    Product, ProductImage, Factura, DetalleFactura, 
    Banner, Category, Configuracion, ProductVariant
)
from store.utils.email import enviar_factura  # ✅ Función oficial de envío

# =====================================================
# 📊 1. GESTIÓN DE INVENTARIO EN LÍNEA
# =====================================================
class ProductVariantInline(admin.TabularInline):
    """Permite editar el stock de cada talla/color dentro del Producto."""
    model = ProductVariant
    extra = 0
    can_delete = True
    verbose_name = "Inventario de Variante"
    verbose_name_plural = "Matriz de Inventario (Talla/Color)"
    fields = ("talla", "color", "stock")

# =====================================================
# 🖼️ 2. IMÁGENES ADICIONALES
# =====================================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = "Imagen adicional"
    verbose_name_plural = "Imágenes adicionales"
    fields = ("image", "color_vinculado", "thumbnail")   
    readonly_fields = ("thumbnail",)

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px; border-radius:5px; border:1px solid #ddd;"/>', obj.image.url)
        return "-"
    thumbnail.short_description = "Vista previa"

# =====================================================
# 🛍️ 3. PRODUCTO PRINCIPAL
# =====================================================
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
        'talla_buttons',
        'color_buttons',
        'video_url',
        'video_file'
    )
    list_editable = ('discount', 'is_available')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_available', 'category', 'destacado', 'nuevo')
    
    # ✅ Inlines integrados
    inlines = [ProductVariantInline, ProductImageInline]

    # ✅ Acciones masivas
    actions = ['generar_variantes_masivo']

    fieldsets = (
        ("Información básica", {
            "fields": ("name", "slug", "description", "category", "image")
        }),
        ("Precio y stock", {
            "fields": ("cost", "discount", "final_price", "stock", "is_available")
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
            "fields": ("date_register", "date_update"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("final_price", "date_register", "date_update")

    # --- MÉTODOS DE BOTONES (Tus funciones originales con estilo mejorado) ---
    def talla_buttons(self, obj):
        if not obj.talla_list: return "-"
        return format_html_join(
            '',
            '<span style="margin:2px; padding:4px 8px; border-radius:4px; background:#f0f0f0; border:1px solid #ccc; display:inline-block; font-size:11px;">{}</span>',
            ((t,) for t in obj.talla_list)
        )
    talla_buttons.short_description = "Tallas"

    def color_buttons(self, obj):
        if not obj.color_list: return "-"
        return format_html_join(
            '',
            '<span style="margin:2px; padding:4px 8px; border-radius:4px; background:#e3f2fd; border:1px solid #90caf9; display:inline-block; font-size:11px;">{}</span>',
            ((c,) for c in obj.color_list)
        )
    color_buttons.short_description = "Colores"

    # --- ACCIÓN PARA GENERAR VARIANTES ---
    @admin.action(description="🚀 Generar combinaciones de Talla/Color masivamente")
    def generar_variantes_masivo(self, request, queryset):
        conteo = 0
        for prod in queryset:
            tallas = prod.talla_list
            colores = prod.color_list
            if not tallas and not colores:
                _, created = ProductVariant.objects.get_or_create(
                    product=prod, talla="", color="", defaults={'stock': prod.stock}
                )
                if created: conteo += 1
            else:
                for t in tallas:
                    for c in colores:
                        _, created = ProductVariant.objects.get_or_create(
                            product=prod, talla=t, color=c, defaults={'stock': 0}
                        )
                        if created: conteo += 1
        self.message_user(request, f"Se crearon {conteo} combinaciones de inventario.", messages.SUCCESS)

# =====================================================
# 🧾 4. FACTURACIÓN (LÓGICA DE REENVÍO COMPLETA)
# =====================================================
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'usuario', 'fecha', 'total', 'metodo_pago', 
        'estado_pago', 'estado_pedido', 'banco', 'correo_enviado'
    )
    date_hierarchy = 'fecha'
    search_fields = ('usuario__username', 'usuario__email', 'nombre', 'email', 'telefono', 'transaccion_id')
    list_filter = ('estado_pago', 'estado_pedido', 'metodo_pago', 'banco', 'correo_enviado')
    
    actions = ["reenviar_factura"]

    def reenviar_factura(self, request, queryset):
        reenviadas = 0
        for factura in queryset:
            if factura.estado_pago == "Pagado" and enviar_factura(factura):
                reenviadas += 1
        self.message_user(request, f"Se reenviaron {reenviadas} factura(s).", messages.SUCCESS)
    reenviar_factura.short_description = "📧 Reenviar factura seleccionada"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:factura_id>/reenviar/', self.admin_site.admin_view(self.reenviar_factura_individual), name='store_factura_reenviar'),
        ]
        return custom_urls + urls

    def reenviar_factura_individual(self, request, factura_id):
        factura = Factura.objects.get(pk=factura_id)
        if factura.estado_pago == "Pagado":
            if enviar_factura(factura):
                self.message_user(request, f"✅ Factura #{factura.id} reenviada correctamente.", messages.SUCCESS)
            else:
                self.message_user(request, f"❌ Error al reenviar factura #{factura.id}.", messages.ERROR)
        else:
            self.message_user(request, f"⚠️ La factura #{factura.id} no está pagada.", messages.WARNING)
        return redirect(f"/admin/store/factura/{factura_id}/change/")

# =====================================================
# 📦 5. OTROS MODELOS
# =====================================================
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura', 'producto', 'cantidad', 'talla', 'color', 'subtotal')
    list_select_related = ('factura', 'producto')
    search_fields = ('producto__name', 'factura__usuario__username')
    list_filter = ('talla', 'color')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "image")
    search_fields = ("title", "subtitle")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'talla', 'color', 'stock')
    list_editable = ('stock',)
    search_fields = ('product__name', 'talla', 'color')
    list_filter = ('product',)

@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ("id", "iva_activo") # Ajustado para que no de error si no hay iva_activo