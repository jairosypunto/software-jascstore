from django.urls import path
from . import views

app_name = 'home'  # ✅ Esto permite usar 'home:home' como nombre completo

urlpatterns = [
    path('', views.home, name='home'),  # ✅ Esta es la ruta que falta
]