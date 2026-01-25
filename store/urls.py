from django.urls import path, include
from . import views
from store.views import generar_factura_pdf

app_name = 'store'

urlpatterns = [
    # 🏬 Tienda y Productos
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle_producto'),
    path('vista-rapida/<int:id>/', views.vista_rapida, name='vista_rapida'),

    # 🛒 Carrito (Gestión Principal)
    path('carrito/', views.ver_carrito, name='ver_carrito'), # Siempre poner la lista antes que las acciones con parámetros
    path('agregar/<int:product_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/eliminar/<str:item_key>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<str:item_key>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito-json/', views.obtener_carrito_json, name='carrito_json'),
    path('carrito-modal/<int:product_id>/', views.carrito_modal, name='carrito_modal'),

    # 💳 Proceso de Pago (Checkout)
    # Si te da 404, asegúrate de que el enlace en el HTML sea {% url 'store:checkout' %}
    path('checkout/', views.checkout, name='checkout'), 
    path('pago-banco/', views.pago_banco_widget, name='pago_banco_widget'),
    path('simular-pago-banco/', views.simular_pago_banco, name='simular_pago_banco'),
    path('confirmacion-pago/', views.confirmacion_pago, name='confirmacion_pago'),

# 📄 Facturación
    path('generar-factura/', views.generar_factura, name='generar_factura'),
    path('mis-facturas/', views.mis_facturas, name='mis_facturas'),
    # Cambiamos el name a 'detalle_factura' para que coincida con tus templates y no de error
    path('factura/<int:factura_id>/', views.ver_factura, name='detalle_factura'),
    path('factura/pdf/<int:factura_id>/', generar_factura_pdf, name='generar_factura_pdf'),

    # 👤 Información y Cuentas
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),
    path('pedidos/', include('pedidos.urls')), # Verifica que pedidos.urls no tenga rutas que choquen
]