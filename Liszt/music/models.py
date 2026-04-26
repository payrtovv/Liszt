from django.db import models


class Discografica(models.Model):
    iddiscografica = models.IntegerField(db_column='idDiscografica', primary_key=True)
    nombrediscografica = models.CharField(db_column='nombreDiscografica', max_length=35, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'Discografica'


class Genero(models.Model):
    idgenero = models.IntegerField(db_column='idGenero', primary_key=True)
    nombre = models.CharField(max_length=80, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'Genero'


class Artista(models.Model):
    idpersona = models.ForeignKey(
        'users.Persona',
        on_delete=models.DO_NOTHING,
        db_column='idPersona'
    )
    idartista = models.IntegerField(db_column='idArtista', primary_key=True)
    discografica = models.ForeignKey(
        'Discografica',
        on_delete=models.DO_NOTHING,
        db_column='Discografica_idDiscografica'
    )
    biografia = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'Artista'


class Lanzamiento(models.Model):
    idlanzamiento = models.IntegerField(db_column='idLanzamiento', primary_key=True)
    artista = models.ForeignKey(
        'Artista',
        on_delete=models.DO_NOTHING,
        db_column='idArtista'
    )
    nombre = models.CharField(db_column='Nombre', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')
    fechadepublicacion = models.DateField(db_column='FechaDePublicacion')
    tipodelanzamiento = models.CharField(db_column='tipoDeLanzamiento', max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS')
    urlportadalanzamiento = models.CharField(db_column='urlPortadaLanzamiento', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Lanzamiento'


class Cancion(models.Model):
    idcancion = models.IntegerField(db_column='idCancion', primary_key=True)
    nombre = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    duracion = models.IntegerField()
    lanzamiento = models.ForeignKey(
        'Lanzamiento',
        on_delete=models.DO_NOTHING,
        db_column='Lanzamiento_idLanzamiento'
    )
    numerodepista = models.IntegerField(db_column='NumeroDePista')
    url_audio = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')
    reproducciones = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Cancion'


class Playlist(models.Model):
    idplaylist = models.IntegerField(db_column='idPlaylist', primary_key=True)
    nombreplaylist = models.CharField(db_column='nombrePlaylist', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')
    usuario = models.ForeignKey(
        'users.Usuario',
        on_delete=models.DO_NOTHING,
        db_column='Usuario_idUsuario'
    )

    class Meta:
        managed = False
        db_table = 'Playlist'


class Regalias(models.Model):
    id_regalia = models.IntegerField(db_column='id_Regalia', primary_key=True)
    monto = models.FloatField()
    fecha = models.DateField()
    artista = models.ForeignKey(
        'Artista',
        on_delete=models.DO_NOTHING,
        db_column='Artista_idArtista'
    )
    cancion = models.ForeignKey(
        'Cancion',
        on_delete=models.DO_NOTHING,
        db_column='Cancion_idCancion'
    )

    class Meta:
        managed = False
        db_table = 'Regalias'


class Artistagenero(models.Model):
    artista = models.ForeignKey(
        'Artista',
        on_delete=models.DO_NOTHING,
        db_column='Artista_idPersona'
    )
    genero = models.ForeignKey(
        'Genero',
        on_delete=models.DO_NOTHING,
        db_column='Genero_idGenero'
    )

    class Meta:
        managed = False
        db_table = 'ArtistaGenero'