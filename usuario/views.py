# 📦 Importaciones estándar de Django
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView

# 📊 Funciones de agregación para métricas
from django.db.models import Sum

# 🧾 Formularios personalizados
from .forms import LoginForm, UserRegistrationForm

# 📦 Modelos de pedidos y productos
from pedidos.models import Order   # ✅ usamos Order, no Pedido
from store.models import Product, Factura

# 👤 Modelo de usuario activo
User = get_user_model()


# 🏠 Vista principal del sitio (portada en "/")
def inicio(request):
    return render(request, 'store/index.html', {'section': 'inicio'})


# 🔐 Vista de inicio de sesión
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


# 🧑‍💼 Vista del dashboard privado con métricas y pedidos
@login_required
def dashboard(request):
    usuario = request.user

    # 🔢 Métricas
    total_pedidos = Factura.objects.filter(usuario=usuario).count()
    productos_publicados = Product.objects.filter(is_available=True).count()

    # 💰 Suma total de ventas reales (solo facturas pagadas)
    total_ventas = (
        Factura.objects.filter(usuario=usuario, estado_pago="Pagado")
        .aggregate(total=Sum('total'))['total']
        or 0
    )

    # 📋 Últimos pedidos (los 5 más recientes)
    pedidos_recientes = (
        Factura.objects.filter(usuario=usuario)
        .order_by('-fecha')[:5]
    )

    # 📦 Productos publicados (no tocar color_list aquí)
    productos = Product.objects.filter(is_available=True)

    context = {
        'section': 'dashboard',
        'total_pedidos': total_pedidos,
        'productos_publicados': productos_publicados,
        'total_ventas': total_ventas,
        'pedidos_recientes': pedidos_recientes,
        'products': productos,  # se usan las @property en la plantilla
    }
    return render(request, 'account/dashboard.html', context)

# 📝 Vista de registro de usuario
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # ✅ Crear usuario nuevo sin guardar aún
            new_user = user_form.save(commit=False)
            # ✅ Asignar contraseña encriptada
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.save()

            # ✅ Loguear automáticamente al nuevo usuario
            login(request, new_user)

            # ✅ Redirigir a la página principal
            return redirect('/home/')
    else:
        user_form = UserRegistrationForm()

    return render(request, 'account/register.html', {'user_form': user_form})