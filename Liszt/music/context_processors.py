from django.db import connection


def sidebar_data(request):
    id_persona = request.session.get('idPersona')
    if not id_persona:
        return {}

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT nombre FROM [usuarios].[Persona] WHERE idPersona = %s",
            [id_persona]
        )
        row = cursor.fetchone()
        nombre_usuario = row[0] if row else '?'

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.idCancion, c.nombre, c.duracion,
                   p.nombre + ' ' + p.apellido AS artista
            FROM [musica].[Cancion] c
            INNER JOIN [musica].[Lanzamiento] l ON l.idLanzamiento = c.Lanzamiento_idLanzamiento
            INNER JOIN [musica].[Artista] a ON a.idArtista = l.idArtista
            INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
            ORDER BY c.reproducciones DESC
        """)
        sidebar_canciones = [
            {
                'id': r[0],
                'titulo': r[1],
                'duracion': f"{r[2] // 60}:{r[2] % 60:02d}" if r[2] else '0:00',
                'artista': r[3],
            }
            for r in cursor.fetchall()
        ]

    return {
        'nombre_usuario': nombre_usuario,
        'sidebar_canciones': sidebar_canciones,
    }
