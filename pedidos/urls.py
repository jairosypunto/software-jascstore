from django.urls import path
from . import views

urlpatterns = [
    path('confirmar_pago/', views.confirmar_pago, name='confirmar_pago'),
    path('factura/<int:order_id>/', views.factura, name='factura'),
]