from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # 🛍️ Ruta principal de la tienda: /store/
    path('', views.store, name='store'),

    # 🗂️ Ruta para filtrar productos por categoría usando slug: /store/category/electronica/
    path('category/<str:category_slug>/', views.store, name='productos_por_categoria'),
]