from django.urls import path
from . import views

urlpatterns = [
    path('artistas/', views.artistas_list, name='artistas'),
    path('artistas/<int:artista_id>/', views.artista_detail, name='artista_detail'),
    path('artistas/<int:artista_id>/editar/', views.artista_editar, name='artista_editar'),
    path('lanzamientos/crear/', views.lanzamiento_crear, name='lanzamiento_crear'),
    path('lanzamientos/<str:lanzamiento_id>/', views.lanzamiento_detail, name='lanzamiento_detail'),
    path('lanzamientos/<str:lanzamiento_id>/canciones/agregar/', views.cancion_crear, name='cancion_crear'),
    path('canciones/<str:cancion_id>/eliminar/', views.cancion_eliminar, name='cancion_eliminar'),
    path('lanzamientos/<int:lanzamiento_id>/canciones/agregar/', views.cancion_crear, name='cancion_crear'),
    path('canciones/', views.canciones_buscar, name='canciones'),
    path('canciones/<int:cancion_id>/stream/', views.stream_cancion, name='stream_cancion'),
    path('generos/', views.generos_list, name='generos'),
    path('generos/<int:genero_id>/', views.genero_detail, name='genero_detail'),
    path('discograficas/', views.discograficas_list, name='discograficas'),
    path('home', views.Home, name='home'),
    # Playlists
    path('playlists/crear/', views.playlist_crear, name='playlist_crear'),
    path('playlists/<str:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('playlists/<str:playlist_id>/editar/', views.playlist_editar, name='playlist_editar'),
    path('playlists/<str:playlist_id>/eliminar/', views.playlist_eliminar, name='playlist_eliminar'),
    path('playlists/<str:playlist_id>/agregar/', views.playlist_agregar_cancion, name='playlist_agregar_cancion'),
    path('playlists/<str:playlist_id>/quitar/<str:cancion_id>/', views.playlist_quitar_cancion, name='playlist_quitar_cancion'),
]