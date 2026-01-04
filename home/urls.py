from django.urls import path
from . import views
from .views import debug_storage, debug_fields_storage


app_name = 'home'  # ✅ Esto permite usar 'home:home' como nombre completo

urlpatterns = [
    path('', views.home, name='home'),  # ✅ Esta es la ruta que falta
    path("debug-storage/", debug_storage),
     path("debug-fields-storage/", debug_fields_storage),

]