from datetime import date

from django.db import connection, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone




# Create your views here.
def index(request):
    return HttpResponse("prueba")

def HomeView(request):
    id_persona = request.session.get('idPersona')

    if not id_persona:
        return redirect('login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nombre, apellido, correo, paisdeorigen
            FROM [Usuarios].[Persona]
            WHERE idPersona = %s
        """, [id_persona])
        row = cursor.fetchone()
        print(row)  # lo ves en la terminal

    return render(request, "users/home.html")

def LoginView(request):
    if request.method == 'POST':
        mail = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT idPersona, contrasenia 
                FROM [Usuarios].[Persona]
                WHERE correo = %s       
            """, [mail])

            row = cursor.fetchone()

            if row is None:
                return render(request, "users/login.html", {'error': 'Correo no encontrado'})

            if row[1] == contrasenia:
                request.session['idPersona'] = row[0]
                return redirect('home')
            else:
                return render(request, "users/login.html", {'error': 'Contraseña incorrecta'})

    return render(request, "users/login.html")

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

        print(contexto)

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


def RegisterArtist(request):
    
    if request.method == 'POST':
        nombre = request.POST.get('Nombre', '').strip()
        apellido = request.POST.get('Apellido', '').strip()
        correo = request.POST.get('correo', '').strip()
        contrasenia = request.POST.get('contrasenia', '')
        confirmar_contrasenia = request.POST.get('confirmar_contrasenia', '')
        fechadenacimiento = request.POST.get('fechadenacimiento')
        genero = request.POST.get('Genero')
        pais = request.POST.get('PaisDeOrigen', '').strip()
        discografica = request.POST.get('Discografica').strip()
        biografia = request.POST.get('Biografia')
        generos_raw = request.POST.get('generos', '')
        print(type(generos_raw))  # ver el tipo
        print(repr(generos_raw))  
        generos = request.POST.get('generos', '').split(',')

        generos = [g.strip() for g in generos if g.strip()]        
        nombreArtistico = request.POST.get('NombreArtistico', '').strip() 
        
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
                
                cursor.execute("SELECT idDiscografica FROM [musica].[Discografica] where nombreDiscografica = %s", [discografica])
                row = cursor.fetchone() 
                
                if row is None:
                    raise ValueError("Discografica no encontrada")
                
                id_discografica = row[0]

                
                cursor.execute("""
                    INSERT INTO [musica].[Artista](
                        idpersona,
                        NombreArtistico,
                        Discografica_idDiscografica,
                        biografia
                    )values(%s,%s,%s,%s)
                    
                    SELECT CONVERT(int, SCOPE_IDENTITY());
                    """
                ,[
                    nuevo_id_persona,
                    nombreArtistico,
                    id_discografica,
                    biografia
                ])
                
                
                for x in generos:
                    cursor.execute("SELECT idGenero from [musica].[Genero] where nombre = %s", [x])
                    row = cursor.fetchone()
                    print(row)
                    if row is None:
                        raise ValueError("Genero no encontrada")
                
                    
                    if row:
                        id_genero = row[0]
                        cursor.execute("""
                                INSERT INTO [relaciones].[ArtistaGenero](
                                    Artista_idPersona,
                                    Genero_idGenero
                                )values(%s,%s)
                                """,[nuevo_id_persona, id_genero ])


    return render(request, 'users/RegisterArtist.html')