from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'payment_method', 'total', 'is_paid', 'is_confirmed', 'created_at')
    list_filter = ('payment_method', 'is_paid', 'is_confirmed')
    search_fields = ('user__username', 'id')