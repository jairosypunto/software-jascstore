from django.contrib import admin
from .models import Order

# ❌ ELIMINADO: @admin.register(Product) 
# Ya que Product se administra desde store/admin.py para evitar el error AlreadyRegistered.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Mostramos los campos que tenías, asegurándonos de que coincidan con tu modelo Order
    list_display = (
        'id', 
        'user', 
        'created_at', 
        'status', # Usamos status que definimos en models.py
        'total_display' # Una función para mostrar el total bonito si lo tienes en el modelo
    )
    
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    # Esto permite ver los productos dentro del pedido en el admin (Opcional pero recomendado)
    filter_horizontal = ('products',)

    def total_display(self, obj):
        # Si tienes un campo o método total en tu modelo Order
        return f"${obj.id}" # Ajusta esto según el campo de total que tengas
    total_display.short_description = "Total"