import os
from django.conf import settings
from django.http import Http404, FileResponse
from django.db import connection, transaction
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from bson import ObjectId
from Liszt.mongodb import db

def _get_id_persona(request):
    return request.session.get('idPersona')


def _get_artista_id(id_persona):
    if not id_persona:
        return None
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT idArtista FROM [musica].[Artista] WHERE idPersona = %s",
            [id_persona]
        )
        row = cursor.fetchone()
    return row[0] if row else None


# ─── ARTISTAS ────────────────────────────────────────────────────────────────

def artistas_list(request):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.idArtista, p.nombre, p.apellido, d.nombreDiscografica,
                   a.biografia, p.paisDeOrigen,
                   (SELECT STRING_AGG(g.nombre, ', ')
                    FROM [relaciones].[ArtistaGenero] ag
                    INNER JOIN [musica].[Genero] g ON g.idGenero = ag.Genero_idGenero
                    WHERE ag.Artista_idPersona = a.idPersona) AS generos
            FROM [musica].[Artista] a
            INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
            INNER JOIN [musica].[Discografica] d ON d.idDiscografica = a.Discografica_idDiscografica
            ORDER BY p.nombre
        """)
        rows = cursor.fetchall()

    artistas = [
        {
            'idArtista': r[0],
            'nombre': r[1],
            'apellido': r[2],
            'discografica': r[3],
            'biografia': r[4],
            'pais': r[5],
            'generos': r[6] or '',
        }
        for r in rows
    ]

    return render(request, 'music/artistas_list.html', {'artistas': artistas})


def artista_detail(request, artista_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    mi_artista_id = _get_artista_id(id_persona)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.idArtista, a.idPersona, p.nombre, p.apellido,
                   p.correo, p.paisDeOrigen, d.nombreDiscografica, a.biografia
            FROM [musica].[Artista] a
            INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
            INNER JOIN [musica].[Discografica] d ON d.idDiscografica = a.Discografica_idDiscografica
            WHERE a.idArtista = %s
        """, [artista_id])
        row = cursor.fetchone()

    if not row:
        return redirect('artistas')

    artista = {
        'idArtista': row[0],
        'idPersona': row[1],
        'nombre': row[2],
        'apellido': row[3],
        'correo': row[4],
        'pais': row[5],
        'discografica': row[6],
        'biografia': row[7],
    }

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT g.idGenero, g.nombre
            FROM [relaciones].[ArtistaGenero] ag
            INNER JOIN [musica].[Genero] g ON g.idGenero = ag.Genero_idGenero
            WHERE ag.Artista_idPersona = %s
        """, [artista['idPersona']])
        generos = [{'id': r[0], 'nombre': r[1]} for r in cursor.fetchall()]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT l.idLanzamiento, l.Nombre, l.FechaDePublicacion,
                   l.tipoDeLanzamiento, g.nombre AS genero,
                   COUNT(c.idCancion) AS num_canciones
            FROM [musica].[Lanzamiento] l
            INNER JOIN [musica].[Genero] g ON g.idGenero = l.Genero_idGenero
            LEFT JOIN [musica].[Cancion] c ON c.Lanzamiento_idLanzamiento = l.idLanzamiento
            WHERE l.idArtista = %s
            GROUP BY l.idLanzamiento, l.Nombre, l.FechaDePublicacion, l.tipoDeLanzamiento, g.nombre
            ORDER BY l.FechaDePublicacion DESC
        """, [artista_id])
        lanzamientos = [
            {
                'idLanzamiento': r[0],
                'nombre': r[1],
                'fecha': r[2],
                'tipo': r[3],
                'genero': r[4],
                'num_canciones': r[5],
            }
            for r in cursor.fetchall()
        ]

    es_propio = (mi_artista_id == artista_id)

    return render(request, 'music/artista_detail.html', {
        'artista': artista,
        'generos': generos,
        'lanzamientos': lanzamientos,
        'es_propio': es_propio,
    })


def artista_editar(request, artista_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    mi_artista_id = _get_artista_id(id_persona)
    if mi_artista_id != artista_id:
        return redirect('artista_detail', artista_id=artista_id)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT idDiscografica, nombreDiscografica FROM [musica].[Discografica] ORDER BY nombreDiscografica"
        )
        discograficas = [{'id': r[0], 'nombre': r[1]} for r in cursor.fetchall()]

    if request.method == 'POST':
        biografia = request.POST.get('biografia', '').strip()
        id_discografica = request.POST.get('discografica')

        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC [musica].[sp_ActualizarArtista] @idArtista = %s, @idDiscografica = %s, @biografia = %s",
                [artista_id, id_discografica, biografia]
            )
        return redirect('artista_detail', artista_id=artista_id)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.idArtista, a.idPersona, p.nombre, p.apellido,
                   p.correo, p.paisDeOrigen, d.nombreDiscografica, a.biografia
            FROM [musica].[Artista] a
            INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
            INNER JOIN [musica].[Discografica] d ON d.idDiscografica = a.Discografica_idDiscografica
            WHERE a.idArtista = %s
        """, [artista_id])
        row = cursor.fetchone()

    artista = {
        'idArtista': row[0],
        'nombre': row[2],
        'apellido': row[3],
        'discografica': row[6],
        'biografia': row[7],
    }

    return render(request, 'music/artista_editar.html', {
        'artista': artista,
        'discograficas': discograficas,
    })


# ─── LANZAMIENTOS ─────────────────────────────────────────────────────────────

def lanzamiento_detail(request, lanzamiento_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    mi_artista_id = _get_artista_id(id_persona)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT l.idLanzamiento, l.Nombre, l.FechaDePublicacion, l.tipoDeLanzamiento,
                   l.urlPortadaLanzamiento, g.nombre AS genero,
                   p.nombre + ' ' + p.apellido AS artista, l.idArtista
            FROM [musica].[Lanzamiento] l
            INNER JOIN [musica].[Genero] g ON g.idGenero = l.Genero_idGenero
            INNER JOIN [musica].[Artista] a ON a.idArtista = l.idArtista
            INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
            WHERE l.idLanzamiento = %s
        """, [lanzamiento_id])
        row = cursor.fetchone()

    if not row:
        return redirect('artistas')

    lanzamiento = {
        'idLanzamiento': row[0],
        'nombre': row[1],
        'fecha': row[2],
        'tipo': row[3],
        'portada': row[4],
        'genero': row[5],
        'artista': row[6],
        'idArtista': row[7],
    }

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT idCancion, nombre, [duración], NumeroDePista, reproducciones
            FROM [musica].[Cancion]
            WHERE Lanzamiento_idLanzamiento = %s
            ORDER BY NumeroDePista
        """, [lanzamiento_id])
        canciones = [
            {
                'idCancion': r[0],
                'nombre': r[1],
                'duracion': f"{r[2] // 60}:{r[2] % 60:02d}",
                'pista': r[3],
                'reproducciones': r[4] or 0,
            }
            for r in cursor.fetchall()
        ]

    es_propio = (mi_artista_id == lanzamiento['idArtista'])

    return render(request, 'music/lanzamiento_detail.html', {
        'lanzamiento': lanzamiento,
        'canciones': canciones,
        'es_propio': es_propio,
    })


def lanzamiento_crear(request):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    usuario_doc = _get_usuario(id_persona)
    if not usuario_doc or not _es_artista(usuario_doc):
        # No tiene perfil de artista -> no puede crear lanzamientos
        return redirect('home')

    perfil_artista = usuario_doc.get("PerfilArtista", {})
    lanzamientos_col = db["Lanzamientos"]
    canciones_col = db["Canciones"]

    lanzamiento_id_sesion = request.session.get('lanzamiento_en_curso')
    lanzamiento_creado = None
    canciones_subidas = []
    error = None
    error_cancion = request.session.pop('error_cancion', None)

    if lanzamiento_id_sesion:
        try:
            lanzamiento_doc = lanzamientos_col.find_one({
                "_id": ObjectId(lanzamiento_id_sesion),
                "IDArtista": ObjectId(id_persona),
            })
        except Exception:
            lanzamiento_doc = None

        if lanzamiento_doc:
            lanzamiento_creado = {
                'idLanzamiento': str(lanzamiento_doc["_id"]),
                'nombre': lanzamiento_doc.get("NombreLanzamiento"),
                'tipo': lanzamiento_doc.get("TipoLanzamiento"),
                'fecha': lanzamiento_doc.get("FechaPublicacion"),
            }

            for c in canciones_col.find(
                {"Lanzamiento.idLanzamiento": lanzamiento_doc["_id"]}
            ).sort("NumeroPista", 1):
                dur = c.get("Duracion") or 0
                canciones_subidas.append({
                    'idCancion': str(c["_id"]),
                    'nombre': c.get("NombreCancion"),
                    'duracion': f"{int(dur) // 60}:{int(dur) % 60:02d}",
                    'pista': c.get("NumeroPista"),
                })

    if request.method == 'POST':
        accion = request.POST.get('accion', '')

        # ── Paso 1: crear lanzamiento ──
        if accion == 'crear_lanzamiento':
            nombre = request.POST.get('nombre', '').strip()
            fecha = request.POST.get('fecha')
            tipo = request.POST.get('tipo')

            if not all([nombre, fecha, tipo]):
                error = 'Todos los campos son obligatorios.'
            else:
                nuevo_doc = {
                    "IDArtista": ObjectId(id_persona),
                    "NombreLanzamiento": nombre,
                    "FechaPublicacion": fecha,
                    "TipoLanzamiento": tipo,
                    "URLPortadaLanzamiento": "",
                }
                resultado = lanzamientos_col.insert_one(nuevo_doc)
                request.session['lanzamiento_en_curso'] = str(resultado.inserted_id)
                request.session.modified = True
                return redirect('lanzamiento_crear')

        # ── Paso 2: subir canción ──
        elif accion == 'subir_cancion' and lanzamiento_id_sesion:
            nombre_cancion = request.POST.get('nombre', '').strip()
            archivo = request.FILES.get('audio')

            if not nombre_cancion or not archivo:
                error_cancion = 'El nombre y el archivo son obligatorios.'
            else:
                ext = os.path.splitext(archivo.name)[1].lower()
                if ext not in ['.mp3', '.wav', '.ogg', '.flac', '.m4a']:
                    error_cancion = 'Formato no permitido. Usa MP3, WAV, OGG, FLAC o M4A.'
                else:
                    siguiente_pista = canciones_col.count_documents({
                        "Lanzamiento.idLanzamiento": ObjectId(lanzamiento_id_sesion)
                    }) + 1

                    carpeta = os.path.join(settings.MEDIA_ROOT, 'canciones', str(lanzamiento_id_sesion))
                    os.makedirs(carpeta, exist_ok=True)

                    nombre_archivo = f"pista_{siguiente_pista}_{nombre_cancion.replace(' ', '_')}{ext}"
                    ruta_completa = os.path.join(carpeta, nombre_archivo)

                    with open(ruta_completa, 'wb+') as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)

                    url_audio = f"/media/canciones/{lanzamiento_id_sesion}/{nombre_archivo}"

                    duracion = 0
                    try:
                        from mutagen import File as MutagenFile
                        audio_info = MutagenFile(ruta_completa)
                        if audio_info and audio_info.info:
                            duracion = int(audio_info.info.length)
                    except Exception:
                        pass

                    lanzamiento_doc = lanzamientos_col.find_one(
                        {"_id": ObjectId(lanzamiento_id_sesion)}
                    )

                    nueva_cancion = {
                        "NombreCancion": nombre_cancion,
                        "Duracion": duracion,
                        "NumeroPista": siguiente_pista,
                        "URLAudio": url_audio,
                        "Reproducciones": 0,
                        "Lanzamiento": {
                            "idLanzamiento": lanzamiento_doc["_id"],
                            "NombreLanzamiento": lanzamiento_doc.get("NombreLanzamiento"),
                            "TipoLanzamiento": lanzamiento_doc.get("TipoLanzamiento"),
                            "FechaPublicacion": lanzamiento_doc.get("FechaPublicacion"),
                            "URLPortadaLanzamiento": lanzamiento_doc.get("URLPortadaLanzamiento", ""),
                            "Artista": {
                                "idArtista": lanzamiento_doc["IDArtista"],
                                "NombreArtistico": perfil_artista.get("NombreArtistico", ""),
                            },
                        },
                    }
                    canciones_col.insert_one(nueva_cancion)
                    return redirect('lanzamiento_crear')

    return render(request, 'music/lanzamiento_form.html', {
        'lanzamiento_creado': lanzamiento_creado,
        'canciones_subidas': canciones_subidas,
        'error': error,
        'error_cancion': error_cancion,
    })

def lanzamiento_editar(request, lanzamiento_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    mi_artista_id = _get_artista_id(id_persona)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT idLanzamiento, Nombre, FechaDePublicacion,
                   tipoDeLanzamiento, Genero_idGenero, idArtista
            FROM [musica].[Lanzamiento]
            WHERE idLanzamiento = %s
        """, [lanzamiento_id])
        row = cursor.fetchone()

    if not row or row[5] != mi_artista_id:
        return redirect('artistas')

    lanzamiento = {
        'idLanzamiento': row[0],
        'nombre': row[1],
        'fecha': row[2].strftime('%Y-%m-%d') if row[2] else '',
        'tipo': row[3],
        'genero_id': row[4],
    }

    with connection.cursor() as cursor:
        cursor.execute("SELECT idGenero, nombre FROM [musica].[Genero] ORDER BY nombre")
        generos = [{'id': r[0], 'nombre': r[1]} for r in cursor.fetchall()]

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        fecha = request.POST.get('fecha')
        tipo = request.POST.get('tipo')
        genero_id = request.POST.get('genero')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE [musica].[Lanzamiento]
                SET Nombre = %s, FechaDePublicacion = %s,
                    tipoDeLanzamiento = %s, Genero_idGenero = %s
                WHERE idLanzamiento = %s
            """, [nombre, fecha, tipo, genero_id, lanzamiento_id])

        return redirect('lanzamiento_detail', lanzamiento_id=lanzamiento_id)

    return render(request, 'music/lanzamiento_form.html', {
        'lanzamiento': lanzamiento,
        'generos': generos,
        'accion': 'Editar',
    })


def lanzamiento_eliminar(request, lanzamiento_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    mi_artista_id = _get_artista_id(id_persona)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT idArtista FROM [musica].[Lanzamiento] WHERE idLanzamiento = %s",
            [lanzamiento_id]
        )
        row = cursor.fetchone()

    if not row or row[0] != mi_artista_id:
        return redirect('artistas')

    if request.method == 'POST':
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM [pagos].[Regalias]
                    WHERE Cancion_idCancion IN (
                        SELECT idCancion FROM [musica].[Cancion]
                        WHERE Lanzamiento_idLanzamiento = %s
                    )
                """, [lanzamiento_id])
                cursor.execute("""
                    DELETE FROM [musica].[Cancion]
                    WHERE Lanzamiento_idLanzamiento = %s
                """, [lanzamiento_id])
                cursor.execute(
                    "DELETE FROM [musica].[Lanzamiento] WHERE idLanzamiento = %s",
                    [lanzamiento_id]
                )
        return redirect('artista_detail', artista_id=mi_artista_id)

    return redirect('lanzamiento_detail', lanzamiento_id=lanzamiento_id)


# ─── CANCIONES ────────────────────────────────────────────────────────────────

def canciones_buscar(request):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    q = request.GET.get('q', '').strip()
    filtro = request.GET.get('filtro', 'nombre')
    canciones = []

    if q:
        param = f'%{q}%'

        if filtro == 'nombre':
            sql = """
                SELECT c.idCancion, c.nombre, c.[duración], c.reproducciones,
                       l.Nombre AS album, p.nombre + ' ' + p.apellido AS artista,
                       l.idLanzamiento, l.idArtista
                FROM [musica].[Cancion] c
                INNER JOIN [musica].[Lanzamiento] l ON l.idLanzamiento = c.Lanzamiento_idLanzamiento
                INNER JOIN [musica].[Artista] a ON a.idArtista = l.idArtista
                INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
                WHERE c.nombre LIKE %s
                ORDER BY c.reproducciones DESC
            """
            params = [param]

        elif filtro == 'genero':
            sql = """
                SELECT c.idCancion, c.nombre, c.[duración], c.reproducciones,
                       l.Nombre AS album, p.nombre + ' ' + p.apellido AS artista,
                       l.idLanzamiento, l.idArtista
                FROM [musica].[Cancion] c
                INNER JOIN [musica].[Lanzamiento] l ON l.idLanzamiento = c.Lanzamiento_idLanzamiento
                INNER JOIN [musica].[Genero] g ON g.idGenero = l.Genero_idGenero
                INNER JOIN [musica].[Artista] a ON a.idArtista = l.idArtista
                INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
                WHERE g.nombre LIKE %s
                ORDER BY c.reproducciones DESC
            """
            params = [param]

        elif filtro == 'artista':
            sql = """
                SELECT c.idCancion, c.nombre, c.[duración], c.reproducciones,
                       l.Nombre AS album, p.nombre + ' ' + p.apellido AS artista,
                       l.idLanzamiento, l.idArtista
                FROM [musica].[Cancion] c
                INNER JOIN [musica].[Lanzamiento] l ON l.idLanzamiento = c.Lanzamiento_idLanzamiento
                INNER JOIN [musica].[Artista] a ON a.idArtista = l.idArtista
                INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
                WHERE p.nombre LIKE %s OR p.apellido LIKE %s
                ORDER BY c.reproducciones DESC
            """
            params = [param, param]

        else:  # album
            sql = """
                SELECT c.idCancion, c.nombre, c.[duración], c.reproducciones,
                       l.Nombre AS album, p.nombre + ' ' + p.apellido AS artista,
                       l.idLanzamiento, l.idArtista
                FROM [musica].[Cancion] c
                INNER JOIN [musica].[Lanzamiento] l ON l.idLanzamiento = c.Lanzamiento_idLanzamiento
                INNER JOIN [musica].[Artista] a ON a.idArtista = l.idArtista
                INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
                WHERE l.Nombre LIKE %s
                ORDER BY c.NumeroDePista
            """
            params = [param]

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        canciones = [
            {
                'idCancion': r[0],
                'nombre': r[1],
                'duracion': f"{r[2] // 60}:{r[2] % 60:02d}",
                'reproducciones': r[3] or 0,
                'album': r[4],
                'artista': r[5],
                'idLanzamiento': r[6],
            }
            for r in rows
        ]

    return render(request, 'music/canciones_buscar.html', {
        'canciones': canciones,
        'q': q,
        'filtro': filtro,
    })


# ─── GÉNEROS ──────────────────────────────────────────────────────────────────

def generos_list(request):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT g.idGenero, g.nombre,
                   COUNT(DISTINCT l.idLanzamiento) AS num_lanzamientos,
                   COUNT(c.idCancion) AS num_canciones
            FROM [musica].[Genero] g
            LEFT JOIN [musica].[Lanzamiento] l ON l.Genero_idGenero = g.idGenero
            LEFT JOIN [musica].[Cancion] c ON c.Lanzamiento_idLanzamiento = l.idLanzamiento
            GROUP BY g.idGenero, g.nombre
            ORDER BY num_canciones DESC
        """)
        generos = [
            {
                'idGenero': r[0],
                'nombre': r[1],
                'num_lanzamientos': r[2],
                'num_canciones': r[3],
            }
            for r in cursor.fetchall()
        ]

    return render(request, 'music/generos_list.html', {'generos': generos})


def genero_detail(request, genero_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT idGenero, nombre FROM [musica].[Genero] WHERE idGenero = %s",
            [genero_id]
        )
        row = cursor.fetchone()

    if not row:
        return redirect('generos')

    genero = {'idGenero': row[0], 'nombre': row[1]}

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.idCancion, c.nombre, c.[duración], c.reproducciones,
                   l.Nombre AS album, p.nombre + ' ' + p.apellido AS artista,
                   l.idLanzamiento
            FROM [musica].[Cancion] c
            INNER JOIN [musica].[Lanzamiento] l ON l.idLanzamiento = c.Lanzamiento_idLanzamiento
            INNER JOIN [musica].[Artista] a ON a.idArtista = l.idArtista
            INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
            WHERE l.Genero_idGenero = %s
            ORDER BY c.reproducciones DESC
        """, [genero_id])
        canciones = [
            {
                'idCancion': r[0],
                'nombre': r[1],
                'duracion': f"{r[2] // 60}:{r[2] % 60:02d}",
                'reproducciones': r[3] or 0,
                'album': r[4],
                'artista': r[5],
                'idLanzamiento': r[6],
            }
            for r in cursor.fetchall()
        ]

    return render(request, 'music/genero_detail.html', {
        'genero': genero,
        'canciones': canciones,
    })


# ─── DISCOGRÁFICAS ────────────────────────────────────────────────────────────

def discograficas_list(request):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT d.idDiscografica, d.nombreDiscografica,
                   COUNT(DISTINCT a.idArtista) AS num_artistas
            FROM [musica].[Discografica] d
            LEFT JOIN [musica].[Artista] a ON a.Discografica_idDiscografica = d.idDiscografica
            GROUP BY d.idDiscografica, d.nombreDiscografica
            ORDER BY num_artistas DESC
        """)
        discograficas_rows = cursor.fetchall()

    discograficas = []
    for row in discograficas_rows:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.idArtista, p.nombre, p.apellido
                FROM [musica].[Artista] a
                INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
                WHERE a.Discografica_idDiscografica = %s
                ORDER BY p.nombre
            """, [row[0]])
            artistas = [
                {'idArtista': r[0], 'nombre': r[1], 'apellido': r[2]}
                for r in cursor.fetchall()
            ]
        discograficas.append({
            'idDiscografica': row[0],
            'nombre': row[1],
            'num_artistas': row[2],
            'artistas': artistas,
        })

    return render(request, 'music/discograficas_list.html', {'discograficas': discograficas})



def Home(request):
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
        "nombre": usuario_doc.get("Nombre"),
        "apellido": usuario_doc.get("Apellido"),
        "correo": usuario_doc.get("Correo"),
    }

    return render(request, 'music/music_player.html', {
        'usuario': usuario,
        'albumes_recomendados': [],
        'artistas_recomendados': [],
    })

def stream_cancion(request, cancion_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT url_audio FROM [musica].[Cancion] WHERE idCancion = %s",
            [cancion_id]
        )
        row = cursor.fetchone()

    if not row or not row[0]:
        raise Http404

    url_audio = row[0]

    # Si es una URL local /media/... la servimos como FileResponse
    if url_audio.startswith('/media/'):
        ruta = os.path.join(settings.BASE_DIR, url_audio.lstrip('/'))
        if not os.path.exists(ruta):
            raise Http404
        ext = os.path.splitext(ruta)[1].lower()
        content_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
            '.m4a': 'audio/mp4',
        }
        content_type = content_types.get(ext, 'audio/mpeg')
        return FileResponse(open(ruta, 'rb'), content_type=content_type)

    # Si es URL externa, redirigir
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect(row[0])
    return HttpResponseRedirect(url_audio)

def cancion_crear(request, lanzamiento_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    mi_artista_id = _get_artista_id(id_persona)
    if not mi_artista_id:
        return redirect('artistas')

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT idArtista FROM [musica].[Lanzamiento] WHERE idLanzamiento = %s",
            [lanzamiento_id]
        )
        row = cursor.fetchone()

    if not row or row[0] != mi_artista_id:
        return redirect('artistas')

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ISNULL(MAX(NumeroDePista), 0) + 1 FROM [musica].[Cancion] WHERE Lanzamiento_idLanzamiento = %s",
            [lanzamiento_id]
        )
        siguiente_pista = cursor.fetchone()[0]

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        archivo = request.FILES.get('audio')

        if not nombre or not archivo:
            request.session['error_cancion'] = 'El nombre y el archivo son obligatorios.'
            return redirect('lanzamiento_crear')

        ext = os.path.splitext(archivo.name)[1].lower()
        if ext not in ['.mp3', '.wav', '.ogg', '.flac', '.m4a']:
            request.session['error_cancion'] = 'Formato no permitido.'
            return redirect('lanzamiento_crear')

        carpeta = os.path.join(settings.MEDIA_ROOT, 'canciones', str(lanzamiento_id))
        os.makedirs(carpeta, exist_ok=True)

        nombre_archivo = f"pista_{siguiente_pista}_{nombre.replace(' ', '_')}{ext}"
        ruta_completa = os.path.join(carpeta, nombre_archivo)

        with open(ruta_completa, 'wb+') as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)

        url_audio = f"/media/canciones/{lanzamiento_id}/{nombre_archivo}"

        duracion = 0
        try:
            from mutagen import File as MutagenFile
            audio_info = MutagenFile(ruta_completa)
            if audio_info and audio_info.info:
                duracion = int(audio_info.info.length)
        except Exception:
            pass

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO [musica].[Cancion]
                    (nombre, duracion, Lanzamiento_idLanzamiento,
                     NumeroDePista, url_audio, reproducciones)
                VALUES (%s, %s, %s, %s, %s, 0)
            """, [nombre, duracion, lanzamiento_id, siguiente_pista, url_audio])

        # Volver al paso 2
        request.session['lanzamiento_en_curso'] = lanzamiento_id
        return redirect('lanzamiento_crear')

    return redirect('lanzamiento_crear')

def cancion_eliminar(request, cancion_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    canciones_col = db["Canciones"]

    try:
        cancion_doc = canciones_col.find_one({"_id": ObjectId(cancion_id)})
    except Exception:
        cancion_doc = None

    if not cancion_doc:
        return redirect('home')

    idartista_cancion = cancion_doc.get("Lanzamiento", {}).get("Artista", {}).get("idArtista")
    if str(idartista_cancion) != id_persona:
        return redirect('home')

    lanzamiento_id = str(cancion_doc["Lanzamiento"]["idLanzamiento"])

    if request.method == 'POST':
        canciones_col.delete_one({"_id": ObjectId(cancion_id)})

        url_audio = cancion_doc.get("URLAudio")
        if url_audio:
            ruta = os.path.join(settings.BASE_DIR, url_audio.lstrip('/'))
            if os.path.exists(ruta):
                os.remove(ruta)

        return redirect('lanzamiento_crear')

    return redirect('lanzamiento_crear')


# ─── PLAYLISTS ────────────────────────────────────────────────────────────────

def playlist_crear(request):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            playlists_col = db["Playlists"]
            resultado = playlists_col.insert_one({
                "NombrePlaylist": nombre,
                "IDUsuario": ObjectId(id_persona),
                "Canciones": [],
            })
            return redirect('playlist_detail', playlist_id=str(resultado.inserted_id))

    return redirect('home')


def playlist_detail(request, playlist_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    playlists_col = db["Playlists"]
    canciones_col = db["Canciones"]

    try:
        playlist_doc = playlists_col.find_one({
            "_id": ObjectId(playlist_id),
            "IDUsuario": ObjectId(id_persona),
        })
    except Exception:
        playlist_doc = None

    if not playlist_doc:
        return redirect('home')

    playlist = {
        'idPlaylist': str(playlist_doc["_id"]),
        'nombre': playlist_doc.get("NombrePlaylist"),
    }

    # Canciones en la playlist, en orden
    entradas = sorted(playlist_doc.get("Canciones", []), key=lambda e: e.get("Orden", 0))
    ids_en_playlist = [e["IDCancion"] for e in entradas]

    canciones_docs = {
        c["_id"]: c
        for c in canciones_col.find({"_id": {"$in": ids_en_playlist}})
    }

    canciones = []
    for entrada in entradas:
        c = canciones_docs.get(entrada["IDCancion"])
        if not c:
            continue
        dur = c.get("Duracion") or 0
        lanzamiento_info = c.get("Lanzamiento", {})
        canciones.append({
            'idCancion': str(c["_id"]),
            'nombre': c.get("NombreCancion"),
            'duracion': f"{int(dur) // 60}:{int(dur) % 60:02d}",
            'artista': lanzamiento_info.get("Artista", {}).get("NombreArtistico", ""),
            'album': lanzamiento_info.get("NombreLanzamiento", ""),
            'orden': entrada.get("Orden"),
        })

    # Canciones disponibles para agregar (que no estén ya en la playlist)
    canciones_disponibles = []
    for c in canciones_col.find({"_id": {"$nin": ids_en_playlist}}).sort("NombreCancion", 1):
        lanzamiento_info = c.get("Lanzamiento", {})
        canciones_disponibles.append({
            'idCancion': str(c["_id"]),
            'nombre': c.get("NombreCancion"),
            'artista': lanzamiento_info.get("Artista", {}).get("NombreArtistico", ""),
            'album': lanzamiento_info.get("NombreLanzamiento", ""),
        })

    return render(request, 'music/playlist_detail.html', {
        'playlist': playlist,
        'canciones': canciones,
        'canciones_disponibles': canciones_disponibles,
    })


def playlist_editar(request, playlist_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    playlists_col = db["Playlists"]

    try:
        playlist_doc = playlists_col.find_one({
            "_id": ObjectId(playlist_id),
            "IDUsuario": ObjectId(id_persona),
        })
    except Exception:
        playlist_doc = None

    if not playlist_doc:
        return redirect('home')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            playlists_col.update_one(
                {"_id": ObjectId(playlist_id)},
                {"$set": {"NombrePlaylist": nombre}},
            )

    return redirect('playlist_detail', playlist_id=playlist_id)


def playlist_eliminar(request, playlist_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    playlists_col = db["Playlists"]

    try:
        playlist_doc = playlists_col.find_one({
            "_id": ObjectId(playlist_id),
            "IDUsuario": ObjectId(id_persona),
        })
    except Exception:
        playlist_doc = None

    if not playlist_doc:
        return redirect('home')

    if request.method == 'POST':
        playlists_col.delete_one({"_id": ObjectId(playlist_id)})
        return redirect('home')

    return redirect('playlist_detail', playlist_id=playlist_id)


def playlist_agregar_cancion(request, playlist_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    playlists_col = db["Playlists"]

    try:
        playlist_doc = playlists_col.find_one({
            "_id": ObjectId(playlist_id),
            "IDUsuario": ObjectId(id_persona),
        })
    except Exception:
        playlist_doc = None

    if not playlist_doc:
        return redirect('home')

    if request.method == 'POST':
        cancion_id = request.POST.get('cancion_id')
        if cancion_id:
            cancion_oid = ObjectId(cancion_id)
            canciones_actuales = playlist_doc.get("Canciones", [])

            ya_existe = any(e["IDCancion"] == cancion_oid for e in canciones_actuales)

            if not ya_existe:
                siguiente_orden = max([e.get("Orden", 0) for e in canciones_actuales], default=0) + 1
                playlists_col.update_one(
                    {"_id": ObjectId(playlist_id)},
                    {"$push": {"Canciones": {"IDCancion": cancion_oid, "Orden": siguiente_orden}}},
                )

    return redirect('playlist_detail', playlist_id=playlist_id)


def playlist_quitar_cancion(request, playlist_id, cancion_id):
    id_persona = _get_id_persona(request)
    if not id_persona:
        return redirect('Login')

    playlists_col = db["Playlists"]

    try:
        playlist_doc = playlists_col.find_one({
            "_id": ObjectId(playlist_id),
            "IDUsuario": ObjectId(id_persona),
        })
    except Exception:
        playlist_doc = None

    if not playlist_doc:
        return redirect('home')

    if request.method == 'POST':
        playlists_col.update_one(
            {"_id": ObjectId(playlist_id)},
            {"$pull": {"Canciones": {"IDCancion": ObjectId(cancion_id)}}},
        )

    return redirect('playlist_detail', playlist_id=playlist_id)
def _get_usuario(id_persona):
    if not id_persona:
        return None
    try:
        return db["Usuarios"].find_one({"_id": ObjectId(id_persona)})
    except Exception:
        return None


def _es_artista(usuario_doc):
    if not usuario_doc:
        return False
    perfil = usuario_doc.get("PerfilArtista") or {}
    return bool(perfil.get("NombreArtistico"))