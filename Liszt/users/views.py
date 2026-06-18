from datetime import date

from django.contrib.auth.hashers import check_password, make_password
from django.db import connection, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from Liszt.mongodb import db
from bson import ObjectId



def index(request):
    return HttpResponse("prueba")


# Create your views here.



#def HomeView(request):
    #id_persona = request.session.get('idPersona')
    #if not id_persona:
        #return redirect('Login')
    #return redirect('/music/home')

def PerfilView(request):
    id_usuario = request.session.get('idPersona')

    if not id_usuario:
        return redirect('Login')

    usuarios = db["Usuarios"]

    usuario_doc = usuarios.find_one({
        "_id": ObjectId(id_usuario)
    })

    if not usuario_doc:
        return redirect('Login')

    usuario = {
        'nombre': usuario_doc.get('Nombre'),
        'apellido': usuario_doc.get('Apellido'),
        'correo': usuario_doc.get('Correo'),
        'fecha_registro': usuario_doc.get('Fecha_Registro'),
        'genero': usuario_doc.get('Genero'),
        'edad': usuario_doc.get('Edad'),
        'paisDeOrigen': usuario_doc.get('PaisOrigen'),
        'fechaDeNacimiento': usuario_doc.get('FechaNacimiento'),
    }

    return render(request, "users/perfil.html", {'usuario': usuario})

def eliminar_usuario(request):
    id_usuario = request.session.get('idPersona')

    if id_usuario:
        db["Usuarios"].delete_one({
            "_id": ObjectId(id_usuario)
        })

        request.session.flush() 

    return redirect('Login')



def _PerfilUpdateViewSqlLegacy(request):
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
    pais_de_origen = request.POST.get('paisDeOrigen', '').strip()
    fecha_de_nacimiento = request.POST.get('fechaDeNacimiento') or None
    contrasenia_actual = request.POST.get('contrasenia_actual', '')
    contrasenia_nueva = request.POST.get('contrasenia_nueva', '')

    usuarios = db["Usuarios"]

    try:
        usuario_doc = usuarios.find_one({"_id": ObjectId(id_persona)})
    except Exception:
        usuario_doc = None

    if not usuario_doc:
        return redirect('Login')
    
    fecha_nacimiento = date.fromisoformat(fecha_de_nacimiento)
    
    hoy = timezone.localdate()
    
    edad = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) <
        (fecha_nacimiento.month, fecha_nacimiento.day)
    )


    cambios = {
        "Nombre": nombre,
        "Apellido": apellido,
        "Correo": correo,
        "Genero": genero,
        "Edad": edad,
        "PaisOrigen": pais_de_origen,
        "FechaNacimiento": fecha_de_nacimiento,
    }

    if contrasenia_nueva:
        contrasenia_guardada = usuario_doc.get("Contrasenia", "")
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

        cambios["Contrasenia"] = make_password(contrasenia_nueva)

    usuarios.update_one(
        {"_id": ObjectId(id_persona)},
        {"$set": cambios},
    )

    return redirect('perfil')


def LoginView(request):
    if request.method == 'POST':
        mail = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')

        usuarios = db["Usuarios"]

        usuario = usuarios.find_one({"Correo": mail})

        if usuario is None:
            return render(
                request,
                "users/login.html",
                {'error': 'Correo no encontrado'}
            )

        if check_password(contrasenia, usuario["Contrasenia"]):
            request.session['idUsuario'] = str(usuario["_id"])
            request.session['correo'] = usuario["Correo"]
            request.session['idPersona'] = str(usuario["_id"])

            return redirect('/music/home')

        return render(
            request,
            "users/login.html",
            {'error': 'Contraseña incorrecta'}
        )

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

        if not all([nombre, apellido, correo, contrasenia, confirmar_contrasenia,
                    fechadenacimiento, genero, pais]):
            contexto['error'] = 'Todos los campos son obligatorios.'
            return render(request, 'users/Register.html', contexto)

        if contrasenia != confirmar_contrasenia:
            contexto['error'] = 'Las contraseñas no coinciden.'
            return render(request, 'users/Register.html', contexto)

        try:
            fecha_nacimiento = date.fromisoformat(fechadenacimiento)
        except ValueError:
            contexto['error'] = 'Fecha de nacimiento inválida.'
            return render(request, 'users/Register.html', contexto)

        hoy = timezone.localdate()

        edad = hoy.year - fecha_nacimiento.year - (
            (hoy.month, hoy.day) <
            (fecha_nacimiento.month, fecha_nacimiento.day)
        )

        if edad < 15:
            contexto['error'] = 'Debes tener al menos 15 años para registrarte.'
            return render(request, 'users/Register.html', contexto)

        usuarios = db["Usuarios"]

        existe = usuarios.find_one({"Correo": correo})

        if existe:
            contexto['error'] = 'Ya existe una cuenta con ese correo.'
            return render(request, 'users/Register.html', contexto)

        contrasenia_hash = make_password(contrasenia)

        usuarios.insert_one({
            "Nombre": nombre,
            "Apellido": apellido,
            "Correo": correo,
            "Contrasenia": contrasenia_hash,
            "Fecha_Registro": hoy.isoformat(),
            "Genero": genero,
            "Edad": edad,
            "PaisOrigen": pais,
            "FechaNacimiento": fecha_nacimiento.isoformat(),
            "TipoCuenta": "gratuita",

            "Suscripcion": {
                "TipoSuscripcion": "Gratuita",
                "FechaInicioSuscripcion": hoy.isoformat(),
                "EstadoSuscripcion": "Activa"
            },

            "PerfilArtista": {
                "NombreArtistico": "",
                "Biografia": "",
                "Generos": [],
                "Discografia": ""
            },

            "ArtistasSeguidos": [],
            "HistorialPagos": []
        })

        print(fecha_nacimiento.isoformat())

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
                cursor.execute("""
                    SET NOCOUNT ON;
                    INSERT INTO [usuarios].[Suscripcion] (
                        tipoSuscripcion,
                        fechaInicioSuscripcion,
                        estadoSuscripcion
                    )
                    VALUES (%s, %s, %s);
                    SELECT CONVERT(int, SCOPE_IDENTITY());
                """, ["Gratuita", timezone.now(), "Activa"])

                nuevo_id_suscripcion = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO [usuarios].[Usuario] (
                        idPersona,
                        tipoDeCuenta,
                        Suscripcion_idSuscripcion
                    )
                    VALUES (%s, %s, %s)
                """, [nuevo_id_persona, 'gratuita', nuevo_id_suscripcion])
                
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
