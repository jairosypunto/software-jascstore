from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('confirmar_pago/', views.confirmar_pago, name='confirmar_pago'),
    path('factura/<int:order_id>/', views.factura, name='factura'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<int:pedido_id>/', views.ver_pedido, name='ver_pedido'),

    # ✅ Ruta profesional con slug
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle_producto'),
]