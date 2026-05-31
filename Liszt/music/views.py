from django.db import connection, transaction
from django.shortcuts import render, redirect


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
            SELECT idCancion, nombre, duracion, NumeroDePista, reproducciones
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

    mi_artista_id = _get_artista_id(id_persona)
    if not mi_artista_id:
        return redirect('artistas')

    with connection.cursor() as cursor:
        cursor.execute("SELECT idGenero, nombre FROM [musica].[Genero] ORDER BY nombre")
        generos = [{'id': r[0], 'nombre': r[1]} for r in cursor.fetchall()]

    error = None

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        fecha = request.POST.get('fecha')
        tipo = request.POST.get('tipo')
        genero_id = request.POST.get('genero')

        if not all([nombre, fecha, tipo, genero_id]):
            error = 'Todos los campos son obligatorios.'
        else:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SET NOCOUNT ON;
                    INSERT INTO [musica].[Lanzamiento]
                        (idArtista, Genero_idGenero, Nombre, FechaDePublicacion, tipoDeLanzamiento)
                    VALUES (%s, %s, %s, %s, %s);
                    SELECT CONVERT(int, SCOPE_IDENTITY());
                """, [mi_artista_id, genero_id, nombre, fecha, tipo])
                nuevo_id = cursor.fetchone()[0]
            return redirect('lanzamiento_detail', lanzamiento_id=nuevo_id)

    return render(request, 'music/lanzamiento_form.html', {
        'generos': generos,
        'accion': 'Crear',
        'error': error,
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
                SELECT c.idCancion, c.nombre, c.duracion, c.reproducciones,
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
                SELECT c.idCancion, c.nombre, c.duracion, c.reproducciones,
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
                SELECT c.idCancion, c.nombre, c.duracion, c.reproducciones,
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
                SELECT c.idCancion, c.nombre, c.duracion, c.reproducciones,
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
            SELECT c.idCancion, c.nombre, c.duracion, c.reproducciones,
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
    return render(request, 'music/music_player.html')