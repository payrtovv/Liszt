from datetime import date

from django.contrib.auth.hashers import check_password, make_password
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
        return redirect('Login')
    return redirect('/music/home')

def PerfilView(request):
    id_persona = request.session.get('idPersona')

    if not id_persona:
        return redirect('Login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nombre, apellido, correo, fecha_registro, genero, edad,
                   paisDeOrigen, fechaDeNacimiento
            FROM [Usuarios].[Persona]
            WHERE idPersona = %s
        """, [id_persona])
        row = cursor.fetchone()

    if row is None:
        return redirect('Login')

    usuario = {
        'nombre': row[0],
        'apellido': row[1],
        'correo': row[2],
        'fecha_registro': row[3],
        'genero': row[4],
        'edad': row[5],
        'paisDeOrigen': row[6],
        'fechaDeNacimiento': row[7],
    }

    return render(request, "users/perfil.html", {'usuario': usuario})

def PerfilUpdateView(request):
    id_persona = request.session.get('idPersona')

    if not id_persona:
        return redirect('Login')

    if request.method != 'POST':
        return redirect('perfil')

    nombre = request.POST.get('nombre', '').strip()
    apellido = request.POST.get('apellido', '').strip()
    correo = request.POST.get('correo', '').strip()
    genero = request.POST.get('genero', '').strip()
    edad = request.POST.get('edad') or None
    pais_de_origen = request.POST.get('paisDeOrigen', '').strip()
    fecha_de_nacimiento = request.POST.get('fechaDeNacimiento') or None
    contrasenia_actual = request.POST.get('contrasenia_actual', '')
    contrasenia_nueva = request.POST.get('contrasenia_nueva', '')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT contrasenia
            FROM [Usuarios].[Persona]
            WHERE idPersona = %s
        """, [id_persona])
        row = cursor.fetchone()

        if row is None:
            return redirect('Login')

        if contrasenia_nueva:
            contrasenia_guardada = row[0]
            contrasenia_actual_ok = check_password(contrasenia_actual, contrasenia_guardada)

            # Compatibilidad temporal para cuentas creadas antes de hashear.
            if not contrasenia_actual_ok and contrasenia_actual == contrasenia_guardada:
                contrasenia_actual_ok = True

            if not contrasenia_actual_ok:
                usuario = {
                    'nombre': nombre,
                    'apellido': apellido,
                    'correo': correo,
                    'genero': genero,
                    'edad': edad,
                    'paisDeOrigen': pais_de_origen,
                    'fechaDeNacimiento': fecha_de_nacimiento,
                }
                return render(request, "users/perfil.html", {
                    'usuario': usuario,
                    'error': 'La contraseña actual no es correcta.',
                })

            contrasenia_nueva_hash = make_password(contrasenia_nueva)

            cursor.execute("""
                UPDATE [Usuarios].[Persona]
                SET nombre = %s, apellido = %s, correo = %s, genero = %s,
                    edad = %s, paisDeOrigen = %s, fechaDeNacimiento = %s,
                    contrasenia = %s
                WHERE idPersona = %s
            """, [
                nombre, apellido, correo, genero, edad, pais_de_origen,
                fecha_de_nacimiento, contrasenia_nueva_hash, id_persona
            ])
        else:
            cursor.execute("""
                UPDATE [Usuarios].[Persona]
                SET nombre = %s, apellido = %s, correo = %s, genero = %s,
                    edad = %s, paisDeOrigen = %s, fechaDeNacimiento = %s
                WHERE idPersona = %s
            """, [
                nombre, apellido, correo, genero, edad, pais_de_origen,
                fecha_de_nacimiento, id_persona
            ])

    return redirect('perfil')

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

            id_persona = row[0]
            contrasenia_guardada = row[1]
            contrasenia_ok = check_password(contrasenia, contrasenia_guardada)

            # Compatibilidad temporal para usuarios ya guardados con contrasenia en texto plano.
            if not contrasenia_ok and contrasenia == contrasenia_guardada:
                contrasenia_ok = True
                cursor.execute("""
                    UPDATE [Usuarios].[Persona]
                    SET contrasenia = %s
                    WHERE idPersona = %s
                """, [make_password(contrasenia), id_persona])

            if contrasenia_ok:
                request.session['idPersona'] = id_persona
                return redirect('/music/home')
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

        if edad < 15:
            contexto['error'] = 'Debes tener al menos 15 anios para registrarte.'
            return render(request, 'users/Register.html', contexto)

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
                contrasenia_hash = make_password(contrasenia)

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
                    contrasenia_hash,
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

        return redirect('Login')

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
            return render(request, 'users/RegisterArtist.html', contexto)

        if contrasenia != confirmar_contrasenia:
            contexto['error'] = 'Las contraseñas no coinciden.'
            return render(request, 'users/RegisterArtist.html', contexto)

        fecha_nacimiento = date.fromisoformat(fechadenacimiento)
        hoy = timezone.localdate()
        edad = hoy.year - fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )

        if edad < 15:
            contexto['error'] = 'Debes tener al menos 15 anios para registrarte.'
            return render(request, 'users/RegisterArtist.html', contexto)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM [usuarios].[Persona] WHERE correo = %s",
                [correo]
            )
            existe = cursor.fetchone()[0]

        if existe:
            contexto['error'] = 'Ya existe una cuenta con ese correo.'
            return render(request, 'users/RegisterArtist.html', contexto)

        with transaction.atomic():
            with connection.cursor() as cursor:
                contrasenia_hash = make_password(contrasenia)

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
                    contrasenia_hash,
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

        return redirect('Login')

    return render(request, 'users/RegisterArtist.html')
