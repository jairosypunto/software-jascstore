from django.shortcuts import render
from .models import Product  # ✅ Import correcto

def home(request):
    products = Product.objects.filter(is_available=True)
    context = {
        'products': products,
    }
    return render(request, "home/home.html", context)