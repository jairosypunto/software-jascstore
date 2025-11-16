from django.shortcuts import HttpResponse, render

def inicio(request):
    return render(request, 'index.html', {'section': 'inicio'})