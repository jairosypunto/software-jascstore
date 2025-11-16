from django.shortcuts import render
from .models import Category

# ✅ Vista para mostrar lista de categorías
def lista_categorias(request):
    categorias = Category.objects.all()
    return render(request, 'categorias/lista.html', {'categorias': categorias})