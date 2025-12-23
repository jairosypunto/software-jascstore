from django.urls import path, include
from . import views
from store.views import generar_factura_pdf

app_name = 'store'

urlpatterns = [
    # 🏬 Tienda
    path('', views.store, name='store'),
    path('category/<str:category_slug>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('vista-rapida/<int:id>/', views.vista_rapida, name='vista_rapida'),
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle_producto'),

    # 🛒 Carrito
    path('agregar/<int:product_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/actualizar/<int:product_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    
    # 🛒 Modal de carrito (contenido dinámico)
    path('carrito/<int:product_id>/', views.carrito_modal, name='carrito_modal'),

    # 💳 Pago
    path('checkout/', views.checkout, name='checkout'),
    path('simular-pago-banco/', views.simular_pago_banco, name='simular_pago_banco'),
    path('pago-banco/', views.pago_banco_widget, name='pago_banco'),
    path('confirmacion-pago/', views.confirmacion_pago, name='confirmacion_pago'),

    # 📄 Facturación
    path('generar-factura/', views.generar_factura, name='generar_factura'),
    path('mis-facturas/', views.mis_facturas, name='mis_facturas'),
    path('factura/<int:factura_id>/', views.ver_factura, name='ver_factura'),
    path('factura/pdf/<int:factura_id>/', generar_factura_pdf, name='generar_factura_pdf'),

    # 👤 Usuario
    path('login/', views.login_view, name='login'),

    # 📄 Info
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),

    # 📦 Pedidos
    path('pedidos/', include('pedidos.urls')),
]