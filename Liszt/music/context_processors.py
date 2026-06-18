from bson import ObjectId
from django.db import OperationalError, connection

from Liszt.mongodb import db


def _mongo_user(id_persona):
    try:
        return db["Usuarios"].find_one({"_id": ObjectId(id_persona)})
    except Exception:
        return None


def sidebar_data(request):
    id_persona = request.session.get("idPersona")
    if not id_persona:
        return {}

    usuario_doc = _mongo_user(id_persona)
    nombre_usuario = usuario_doc.get("Nombre", "?") if usuario_doc else "?"

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT nombre FROM [usuarios].[Persona] WHERE idPersona = %s",
                [id_persona],
            )
            row = cursor.fetchone()
            if row:
                nombre_usuario = row[0]

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT idArtista FROM [musica].[Artista] WHERE idPersona = %s",
                [id_persona],
            )
            row = cursor.fetchone()
            es_artista = row is not None
            mi_artista_id = row[0] if row else None

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT idUsuario FROM [usuarios].[Usuario] WHERE idPersona = %s",
                [id_persona],
            )
            row = cursor.fetchone()
            id_usuario = row[0] if row else None

        playlists = []
        if id_usuario:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT idPlaylist, nombrePlaylist
                    FROM [usuarios].[Playlist]
                    WHERE Usuario_idUsuario = %s
                    ORDER BY nombrePlaylist
                    """,
                    [id_usuario],
                )
                playlists = [
                    {"id": r[0], "nombre": r[1]}
                    for r in cursor.fetchall()
                ]

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.idCancion, c.nombre, c.duracion,
                       p.nombre || ' ' || p.apellido AS artista
                FROM [musica].[Cancion] c
                INNER JOIN [musica].[Lanzamiento] l ON l.idLanzamiento = c.Lanzamiento_idLanzamiento
                INNER JOIN [musica].[Artista] a ON a.idArtista = l.idArtista
                INNER JOIN [usuarios].[Persona] p ON p.idPersona = a.idPersona
                ORDER BY c.reproducciones DESC
                """
            )
            sidebar_canciones = [
                {
                    "id": r[0],
                    "titulo": r[1],
                    "duracion": f"{r[2] // 60}:{r[2] % 60:02d}" if r[2] else "0:00",
                    "artista": r[3],
                }
                for r in cursor.fetchall()
            ]
    except OperationalError:
        perfil_artista = usuario_doc.get("PerfilArtista", {}) if usuario_doc else {}
        es_artista = bool(perfil_artista.get("NombreArtistico"))
        mi_artista_id = None
        id_usuario = None
        playlists = []
        sidebar_canciones = []

    return {
        "nombre_usuario": nombre_usuario,
        "sidebar_canciones": sidebar_canciones,
        "es_artista": es_artista,
        "mi_artista_id": mi_artista_id,
        "id_usuario": id_usuario,
        "sidebar_playlists": playlists,
    }
