# pedidos/admin.py
from django.contrib import admin
from .models import Order, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'image', 'tallas', 'colores')
    search_fields = ('name',)
    list_filter = ('price',)
    ordering = ('name',)
    fields = ('name', 'price', 'image', 'tallas', 'colores')  # ✅ editable en admin

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'created_at', 'total',
        'payment_method', 'is_paid', 'is_confirmed'
    )
    list_filter = ('is_paid', 'is_confirmed', 'payment_method')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)