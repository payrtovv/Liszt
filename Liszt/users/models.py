# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Persona(models.Model):
    idpersona = models.IntegerField(db_column='idPersona')  # Field name made lowercase.
    nombre = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    apellido = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    correo = models.CharField(max_length=80, db_collation='SQL_Latin1_General_CP1_CI_AS')
    fecha_registro = models.DateField()
    genero = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    edad = models.IntegerField(blank=True, null=True)
    contrasenia = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    verificado = models.BooleanField()
    paisdeorigen = models.CharField(db_column='paisDeOrigen', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    fechadenacimiento = models.DateField(db_column='fechaDeNacimiento')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Persona'



class Pago(models.Model):
    id_pago = models.IntegerField(db_column='id_Pago')  # Field name made lowercase.
    monto = models.FloatField()
    fecha = models.DateField()
    metodo_pago = models.CharField(db_column='metodo_Pago', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    estado_pago = models.CharField(db_column='estado_Pago', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    suscripcion_idsuscripcion = models.IntegerField(db_column='Suscripcion_idSuscripcion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Pago'




class Usuarioartista(models.Model):
    artista_idpersona = models.IntegerField(db_column='Artista_idPersona')  # Field name made lowercase.
    usuario_idpersona = models.IntegerField(db_column='Usuario_idPersona')  # Field name made lowercase.
    notificaciones_activas = models.BooleanField()
    fecha_inicio_seguimiento = models.DateField()

    class Meta:
        managed = False
        db_table = 'UsuarioArtista'



class Suscripcion(models.Model):
    idsuscripcion = models.IntegerField(db_column='idSuscripcion')  # Field name made lowercase.
    tiposuscripcion = models.CharField(db_column='tipoSuscripcion', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    fechainiciosuscripcion = models.DateTimeField(db_column='fechaInicioSuscripcion')  # Field name made lowercase.
    estadosuscripcion = models.CharField(db_column='estadoSuscripcion', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Suscripcion'


class Usuario(models.Model):
    idpersona = models.IntegerField(db_column='idPersona')  # Field name made lowercase.
    idusuario = models.IntegerField(db_column='idUsuario')  # Field name made lowercase.
    tipodecuenta = models.CharField(db_column='tipoDeCuenta', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    suscripcion_idsuscripcion = models.IntegerField(db_column='Suscripcion_idSuscripcion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Usuario'
