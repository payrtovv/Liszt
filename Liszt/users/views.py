from datetime import date

from django.db import connection, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone




# Create your views here.
def index(request):
    return HttpResponse("prueba")

def Register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('Nombre', '').strip()
        apellido = request.POST.get('Apellido', '').strip()
        correo = request.POST.get('correo', '').strip()
        contrasenia = request.POST.get('contrasenia', '')
        confirmar_contrasenia = request.POST.get('confirmar_contrasenia', '')
        fechadenacimiento = request.POST.get('fechadenacimiento')
        genero = request.POST.get('Genero')
        pais = request.POST.get('PaisDeOrigen', '').strip()

        contexto = {
            'Nombre': nombre,
            'Apellido': apellido,
            'correo': correo,
            'fechadenacimiento': fechadenacimiento,
            'Genero': genero,
            'PaisDeOrigen': pais,
        }

        if not all([nombre, apellido, correo, contrasenia, fechadenacimiento, genero, pais]):
            contexto['error'] = 'Todos los campos son obligatorios.'
            return render(request, 'users/Register.html', contexto)

        if contrasenia != confirmar_contrasenia:
            contexto['error'] = 'Las contraseñas no coinciden.'
            return render(request, 'users/Register.html', contexto)

        fecha_nacimiento = date.fromisoformat(fechadenacimiento)
        hoy = timezone.localdate()
        edad = hoy.year - fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM [usuarios].[Persona] WHERE correo = %s",
                [correo]
            )
            existe = cursor.fetchone()[0]

        if existe:
            contexto['error'] = 'Ya existe una cuenta con ese correo.'
            return render(request, 'users/Register.html', contexto)

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    SET NOCOUNT ON;

                    INSERT INTO [usuarios].[Persona] (
                        nombre,
                        apellido,
                        correo,
                        fecha_registro,
                        genero,
                        edad,
                        contrasenia,
                        verificado,
                        paisDeOrigen,
                        fechaDeNacimiento
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

                    SELECT CONVERT(int, SCOPE_IDENTITY());
                """, [
                    nombre,
                    apellido,
                    correo,
                    hoy,
                    genero,
                    edad,
                    contrasenia,
                    False,
                    pais,
                    fecha_nacimiento,
                ])

                nuevo_id_persona = cursor.fetchone()[0]

                cursor.execute("""
                    SET NOCOUNT ON;

                    INSERT INTO [usuarios].[Suscripcion] (
                        tipoSuscripcion,
                        fechaInicioSuscripcion,
                        estadoSuscripcion
                    )
                    VALUES (%s, %s, %s);

                    SELECT CONVERT(int, SCOPE_IDENTITY());
                """, [
                    "Gratuita",
                    timezone.now(),
                    "Activa"
                ])

                nuevo_id_suscripcion = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO [usuarios].[Usuario] (
                        idPersona,
                        tipoDeCuenta,
                        Suscripcion_idSuscripcion
                    )
                    VALUES (%s, %s, %s)
                """, [
                    nuevo_id_persona,
                    'gratuita',
                    nuevo_id_suscripcion
                ])


    return render(request, 'users/Register.html')
