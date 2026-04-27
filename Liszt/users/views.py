from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Persona


# Create your views here.
def index(request):
    return HttpResponse("prueba")


def login_view(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contrasenia = request.POST['contrasenia']
        try:
            persona = Persona.objects.get(correo=correo, contrasenia=contrasenia)
            request.session['usuario_id'] = persona.idpersona
            return redirect('home')
        except Persona.DoesNotExist:
            return render(request, 'users/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'users/login.html')
