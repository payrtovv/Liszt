from django.db import models

# Create your models here.
class Cancion(models.Model):
    idcancion = models.IntegerField(db_column='idCancion')  # Field name made lowercase.
    nombre = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    duracion = models.IntegerField()
    lanzamiento_idlanzamiento = models.IntegerField(db_column='Lanzamiento_idLanzamiento')  # Field name made lowercase.
    numerodepista = models.IntegerField(db_column='NumeroDePista')  # Field name made lowercase.
    url_audio = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')
    reproducciones = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Cancion'

class Discografica(models.Model):
    iddiscografica = models.IntegerField(db_column='idDiscografica')  # Field name made lowercase.
    nombrediscografica = models.CharField(db_column='nombreDiscografica', max_length=35, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Discografica'


class Genero(models.Model):
    idgenero = models.IntegerField(db_column='idGenero')  # Field name made lowercase.
    nombre = models.CharField(max_length=80, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'Genero'


class Lanzamiento(models.Model):
    idlanzamiento = models.IntegerField(db_column='idLanzamiento')  # Field name made lowercase.
    idartista = models.IntegerField(db_column='idArtista')  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    fechadepublicacion = models.DateField(db_column='FechaDePublicacion')  # Field name made lowercase.
    tipodelanzamiento = models.CharField(db_column='tipoDeLanzamiento', max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    urlportadalanzamiento = models.CharField(db_column='urlPortadaLanzamiento', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Lanzamiento'


class Playlist(models.Model):
    idplaylist = models.IntegerField(db_column='idPlaylist')  # Field name made lowercase.
    nombreplaylist = models.CharField(db_column='nombrePlaylist', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    usuario_idusuario = models.IntegerField(db_column='Usuario_idUsuario')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Playlist'


class Artista(models.Model):
    idpersona = models.IntegerField(db_column='idPersona')  # Field name made lowercase.
    idartista = models.IntegerField(db_column='idArtista')  # Field name made lowercase.
    discografica_iddiscografica = models.IntegerField(db_column='Discografica_idDiscografica')  # Field name made lowercase.
    biografia = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'Artista'

class Regalias(models.Model):
    id_regalia = models.IntegerField(db_column='id_Regalia')  # Field name made lowercase.
    monto = models.FloatField()
    fecha = models.DateField()
    artista_idartista = models.IntegerField(db_column='Artista_idArtista')  # Field name made lowercase.
    cancion_idcancion = models.IntegerField(db_column='Cancion_idCancion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Regalias'



class Artistagenero(models.Model):
    artista_idpersona = models.IntegerField(db_column='Artista_idPersona')  # Field name made lowercase.
    genero_idgenero = models.IntegerField(db_column='Genero_idGenero')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ArtistaGenero'
