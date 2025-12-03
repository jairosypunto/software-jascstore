from django.urls import path
from . import views
from django.urls import path, include
from store.views import generar_factura_pdf


app_name = 'store'

urlpatterns = [
    # 🏬 Tienda y navegación
    path('', views.store, name='store'),  # Página principal de la tienda
    path('category/<str:category_slug>/', views.productos_por_categoria, name='productos_por_categoria'),  # Filtro por categoría
    path('vista-rapida/<int:id>/', views.vista_rapida, name='vista_rapida'),  # Vista rápida de producto
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle_producto'),  # Vista detallada del producto
    
    # 🛒 Carrito y compra
    path('agregar/<int:product_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),  # Agregar producto al carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),  # Ver contenido del carrito
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),  # Vaciar el carrito
    path('checkout/', views.checkout, name='checkout'),  # Proceso de pago
    path('carrito/actualizar/<int:product_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),  # Actualizar cantidad en el carrito

    # 💳 Pago y facturación
    path('confirmar-pago/', views.confirmacion_pago, name='confirmar_pago'),  # Confirmación de pago interno
    path('simular-pago-banco/', views.simular_pago_banco, name='simular_pago_banco'),  # Simulación de pago bancario
    path('pago-banco/', views.pago_banco_widget, name='pago_banco'),  # Flujo real de pago bancario (Wompi)
    path('confirmacion-pago/', views.confirmacion_pago, name='confirmacion_pago'),  # Resultado del pago bancario
    path('generar-factura/', views.generar_factura, name='generar_factura'),  # Generar factura tras pago
    path('mis-facturas/', views.mis_facturas, name='mis_facturas'),  # Ver facturas del usuario
    path('factura/<int:factura_id>/', views.ver_factura, name='ver_factura'),  # Detalle de factura específica
    path('factura/pdf/<int:factura_id>/', generar_factura_pdf, name='generar_factura_pdf'),
    


    # 👤 Usuario y autenticación
    path('login/', views.login_view, name='login'),  # Inicio de sesión

    # 📄 Información institucional
    path('nosotros/', views.nosotros, name='nosotros'),  # Página "Nosotros"
    path('contacto/', views.contacto, name='contacto'),  # Página "Contacto"
    path('pedidos/', include('pedidos.urls')),  # ✅ anidado dentro de store

]