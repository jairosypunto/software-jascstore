from django.contrib import admin
from .models import Order, Product

# 📦 Administración de productos
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'image')  # columnas visibles
    search_fields = ('name',)  # búsqueda por nombre
    list_filter = ('price',)   # filtro por precio
    ordering = ('name',)       # orden alfabético

# 🧾 Administración de pedidos
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'created_at', 'total',
        'payment_method', 'is_paid', 'is_confirmed'
    )  # columnas visibles
    list_filter = ('is_paid', 'is_confirmed', 'payment_method')  # filtros laterales
    search_fields = ('user__username',)  # búsqueda por usuario
    date_hierarchy = 'created_at'  # navegación por fecha
    ordering = ('-created_at',)    # pedidos más recientes primero