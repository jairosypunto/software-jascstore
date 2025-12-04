from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order
from .utils import calcular_total

@login_required
def confirmar_pago(request):
    if request.method == 'POST':
        metodo = request.POST.get('metodo_pago')

        # ✅ Recuperar el carrito desde la sesión
        carrito = request.session.get('carrito', {})
        print("Carrito recibido:", carrito)  # 🧪 Depuración visual

        # ✅ Validar que el carrito no esté vacío
        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('carrito')

        # ✅ Calcular el total solo si el carrito tiene contenido válido
        total = calcular_total(carrito)
        print("Total calculado:", total)  # 🧪 Depuración visual

        # ✅ Crear el pedido en la base de datos
        order = Order.objects.create(
            user=request.user,
            total=total,
            payment_method=metodo,
            is_paid=(metodo == 'transferencia'),
            is_confirmed=True
        )

        messages.success(request, "Pedido confirmado correctamente.")
        return redirect('factura', order_id=order.id)

    # ✅ Renderizar el formulario si no es POST
    return render(request, 'confirmar_pago.html')


@login_required
def factura(request, order_id):
    # ✅ Recuperar el pedido del usuario
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'factura.html', {'order': order})


@login_required
def mis_pedidos(request):
    # Aquí puedes traer los pedidos del usuario autenticado
    # Ejemplo mínimo para que no falle:
    return render(request, 'pedidos/mis_pedidos.html')