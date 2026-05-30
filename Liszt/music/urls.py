from django.urls import path
from . import views

urlpatterns = [
    path('artistas/', views.artistas_list, name='artistas'),
    path('artistas/<int:artista_id>/', views.artista_detail, name='artista_detail'),
    path('artistas/<int:artista_id>/editar/', views.artista_editar, name='artista_editar'),
    path('lanzamientos/crear/', views.lanzamiento_crear, name='lanzamiento_crear'),
    path('lanzamientos/<int:lanzamiento_id>/', views.lanzamiento_detail, name='lanzamiento_detail'),
    path('lanzamientos/<int:lanzamiento_id>/editar/', views.lanzamiento_editar, name='lanzamiento_editar'),
    path('lanzamientos/<int:lanzamiento_id>/eliminar/', views.lanzamiento_eliminar, name='lanzamiento_eliminar'),
    path('canciones/', views.canciones_buscar, name='canciones'),
    path('generos/', views.generos_list, name='generos'),
    path('generos/<int:genero_id>/', views.genero_detail, name='genero_detail'),
    path('discograficas/', views.discograficas_list, name='discograficas'),
]
