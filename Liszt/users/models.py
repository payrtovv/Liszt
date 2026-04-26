from django.db import models


class Persona(models.Model):
    idpersona = models.IntegerField(db_column='idPersona', primary_key=True)
    nombre = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    apellido = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    correo = models.CharField(max_length=80, db_collation='SQL_Latin1_General_CP1_CI_AS')
    fecha_registro = models.DateField()
    genero = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    edad = models.IntegerField(blank=True, null=True)
    contrasenia = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    verificado = models.BooleanField()
    paisdeorigen = models.CharField(db_column='paisDeOrigen', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    fechadenacimiento = models.DateField(db_column='fechaDeNacimiento')

    class Meta:
        managed = False
        db_table = 'Persona'


class Suscripcion(models.Model):
    idsuscripcion = models.IntegerField(db_column='idSuscripcion', primary_key=True)
    tiposuscripcion = models.CharField(db_column='tipoSuscripcion', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    fechainiciosuscripcion = models.DateTimeField(db_column='fechaInicioSuscripcion')
    estadosuscripcion = models.CharField(db_column='estadoSuscripcion', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'Suscripcion'


class Pago(models.Model):
    id_pago = models.IntegerField(db_column='id_Pago', primary_key=True)
    monto = models.FloatField()
    fecha = models.DateField()
    metodo_pago = models.CharField(db_column='metodo_Pago', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')
    estado_pago = models.CharField(db_column='estado_Pago', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')
    suscripcion = models.ForeignKey(
        'Suscripcion',
        on_delete=models.DO_NOTHING,
        db_column='suscripcion_idsuscripcion'
    )

    class Meta:
        managed = False
        db_table = 'Pago'


class Usuario(models.Model):
    idpersona = models.ForeignKey(
        'Persona',
        on_delete=models.DO_NOTHING,
        db_column='idPersona'
    )
    idusuario = models.IntegerField(db_column='idUsuario', primary_key=True)
    tipodecuenta = models.CharField(db_column='tipoDeCuenta', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')
    suscripcion = models.ForeignKey(
        'Suscripcion',
        on_delete=models.DO_NOTHING,
        db_column='Suscripcion_idSuscripcion'
    )

    class Meta:
        managed = False
        db_table = 'Usuario'

class Usuarioartista(models.Model):
    artista = models.ForeignKey(
        'music.Artista',  # ← agregar el nombre de la app
        on_delete=models.DO_NOTHING,
        db_column='Artista_idPersona'
    )
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.DO_NOTHING,
        db_column='Usuario_idPersona'
    )
    notificaciones_activas = models.BooleanField()
    fecha_inicio_seguimiento = models.DateField()

    class Meta:
        managed = False
        db_table = 'UsuarioArtista'