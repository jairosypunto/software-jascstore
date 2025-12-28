from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order
from store.models import Product   # ✅ Importar el modelo correcto
from .utils import calcular_total


@login_required
def confirmar_pago(request):
    if request.method == 'POST':
        metodo = request.POST.get('metodo_pago')
        carrito = request.session.get('carrito', {})
        print("Carrito recibido:", carrito)

        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('carrito')

        total = calcular_total(carrito)
        print("Total calculado:", total)

        order = Order.objects.create(
            user=request.user,
            total=total,
            payment_method=metodo,
            is_paid=(metodo == 'transferencia'),
            is_confirmed=True
        )

        request.session['pedido_id'] = order.id
        messages.success(request, "Pedido confirmado correctamente.")
        return redirect('factura', order_id=order.id)

    return render(request, 'confirmar_pago.html')


@login_required
def factura(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'factura.html', {'order': order})


@login_required
def mis_pedidos(request):
    pedidos = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def ver_pedido(request, pedido_id):
    pedido = get_object_or_404(Order, id=pedido_id, user=request.user)
    detalles = pedido.products.all()
    context = {
        "pedido": pedido,
        "detalles": detalles,
    }
    return render(request, "pedidos/ver_pedido.html", context)


# ✅ Vista profesional con slug para detalle de producto
@login_required
def detalle_producto(request, slug):
    producto = get_object_or_404(Product, slug=slug)
    return render(request, "store/detalle_producto.html", {"producto": producto})


