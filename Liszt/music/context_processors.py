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

    # Playlists desde Mongo (ya no SQL Server)
    playlist = []
    if usuario_doc:
        try:
            playlist = [
                {"id": str(p["_id"]), "nombre": p.get("NombrePlaylist")}
                for p in db["Playlist"].find({"IDUsuario": ObjectId(id_persona)}).sort("NombrePlaylist", 1)
            ]
        except Exception:
            playlist = []

    perfil_artista = usuario_doc.get("PerfilArtista", {}) if usuario_doc else {}
    es_artista = bool(perfil_artista.get("NombreArtistico"))
    mi_artista_id = None
    id_usuario = id_persona  # en Mongo, Persona y Usuario están fusionados

    sidebar_canciones = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT idArtista FROM [musica].[Artista] WHERE idPersona = %s
                """,
                [id_persona],
            )
            row = cursor.fetchone()
            if row:
                mi_artista_id = row[0]
    except Exception:
        pass

    try:
        for c in db["Canciones"].find({}).sort("Reproducciones", -1).limit(20):
            dur = c.get("Duracion") or 0
            lanzamiento_info = c.get("Lanzamiento", {})
            sidebar_canciones.append({
                "id": str(c["_id"]),
                "titulo": c.get("NombreCancion"),
                "duracion": f"{int(dur) // 60}:{int(dur) % 60:02d}",
                "artista": lanzamiento_info.get("Artista", {}).get("NombreArtistico", ""),
            })
    except Exception:
        sidebar_canciones = []

    return {
        "nombre_usuario": nombre_usuario,
        "sidebar_canciones": sidebar_canciones,
        "es_artista": es_artista,
        "mi_artista_id": mi_artista_id,
        "id_usuario": id_usuario,
        "sidebar_playlist": playlist,
    }