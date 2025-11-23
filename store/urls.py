from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<str:category_slug>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('agregar/<int:product_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmar-pago/', views.confirmar_pago, name='confirmar_pago'),
    path('simular-pago-banco/', views.simular_pago_banco, name='simular_pago_banco'),
    path('generar-factura/', views.generar_factura, name='generar_factura'),
     path('login/', views.login_view, name='login'),  # 👈 define el name


    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),

]