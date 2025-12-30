from django.urls import path
from django.contrib.auth import views as auth_views  # Vistas genéricas de autenticación
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # 🔐 Login: muestra formulario y redirige al /home/ si ya está autenticado
    path(
        'login/',
        LoginView.as_view(
            template_name='account/login.html',
            redirect_authenticated_user=True,
            next_page='/home/'  # ✅ Redirección después del login
        ),
        name='login'
    ),

    # 🔓 Logout: cierra sesión y redirige según LOGOUT_REDIRECT_URL en settings.py
    path('logout/', LogoutView.as_view(), name='logout'),

    # 🔑 Cambio de contraseña (requiere estar autenticado)
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # 🔁 Recuperación de contraseña por email
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # 📝 Registro de nuevos usuarios
    path('register/', views.register, name='register'),

    # 🧑 Dashboard del usuario (solo si está autenticado)
    path('dashboard/', views.dashboard, name='dashboard'),  # ✅ Ruta clara y específica

    # 🧪 Rutas futuras (perfil, historial, etc.)
    # path('perfil/', views.perfil, name='perfil'),
]