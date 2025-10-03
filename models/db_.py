# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


# https://web2py.com/books/default/chapter/29/07/forms-and-validators#Custom-validators
class CLAVE_VALIDATOR:
    def __init__(self, error_message='error'):
        self.e = error_message 
    def __call__(self, value, record_id):
        if value:
            where = 'BINARY clave_reparador = \'{}\''.format(value)
            sql = 'SELECT 1 FROM destinatario WHERE ' + where
            res = db.executesql(sql)
            if res:
                return (value, self.e)
        return (value, None)

tabla('info', Field('html'), Field('texto'), migrate=False)

tabla('territorio',
      Field('clave'),
      Field('nombre', notnull=True),
      Field('region_id', 'integer'),
      Field('provincia_id', 'integer'),
      Field('orden', 'integer'),
      format=' %(nombre)s', migrate=False)

tabla('area',
      Field('nombre', notnull=True),
      Field('clave', notnull=True),
      Field('descripcion'),
      Field('territorio_id', 'reference territorio',
            notnull=True, label='Territorio'),
      Field('automatico', 'boolean', notnull=True, default=True),
      Field('sigetp_ct_id', 'integer'),
      Field('sigetp_ct_nombre'),
      format=' %(nombre)s', migrate=False)

tabla('region',
      Field('nombre', notnull=True),
      Field('descripcion'),
      format=' %(nombre)s', migrate=False)

tabla('central',
      Field('nombre', notnull=True),
      Field('area_id', 'reference area', label='Area'),
      Field('region_id', 'reference region', label='Región'),
      format=' %(nombre)s', migrate=False)

tabla('zona',
      Field('nombre', notnull=True),
      Field('descripcion'),
      Field('area_id', 'reference area', notnull=True, label='Area'),
      auth.signature,
      format=' %(nombre)s', migrate=False)

tabla('zona_tp',
      Field('nombre', notnull=True),
      Field('descripcion'),
      Field('area_id', 'reference area', label='Area'),
      format=' %(nombre)s', migrate=False)

tabla('usuario_area',
      Field('area_id', 'reference area', label='Area'),
      Field('usuario_id', 'reference auth_user'), migrate=False)

tabla('grupo',
      Field('nombre', notnull=True),
      Field('descripcion'),
      format=' %(nombre)s - %(descripcion)s', migrate=False)

tabla('usuario_grupo',
      Field('grupo_id', 'reference grupo', label='Area'),
      Field('usuario_id', 'reference auth_user'), migrate=False)

tabla('smsgrupo',
      Field('nombre', notnull=True),
      Field('descripcion'),
      format=' %(nombre)s', migrate=False)

tabla('destinatario',
      Field('nombre', notnull=True),
      Field('apellidos', notnull=True),
      Field('telefono', 'integer', notnull=True, unique=True),
      Field('correo', notnull=False, unique=False),
      Field('pin', 'integer', notnull=True, unique=True),
      Field('activo', 'boolean', notnull=True, default=True),
      Field('clave_reparador', label='Clave'),
      auth.signature,
      format=' %(nombre)s %(apellidos)s', migrate=False)

tabla('destinatario_area',
      Field('destinatario_id', 'reference destinatario', label='Destinatario'),
      Field('area_id', 'reference area', label='Área'), migrate=False)

tabla('destinatario_smsgrupo',
      Field('destinatario_id', 'reference destinatario', label='Destinatario'),
      Field('smsgrupo_id', 'reference smsgrupo', label='Grupo SMS'), migrate=False)

tabla('destinatario_grupo',
      Field('destinatario_id', 'reference destinatario', label='Destinatario'),
      Field('grupo_id', 'reference grupo', label='Grupo'), migrate=False)

tabla('asignacion',
      Field('destinatario_id', 'reference destinatario'),
      Field('central_id', 'reference central'),
      Field('region_id', 'reference region'),
      Field('zona_id', 'reference zona'),
      Field('comienza', 'datetime'),
      Field('termina', 'datetime'),
      auth.signature,
      migrate=False)

tabla('asignacion_tp',
      Field('destinatario_id', 'reference destinatario'),
      Field('zona_id', 'reference zona_tp'),
      Field('comienza', 'datetime'),
      Field('termina', 'datetime'),
      auth.signature,
      migrate=False)

tabla('wsupdate',
      Field('fecha'),
      migrate=False)

tabla('despachado_os',
      Field('idorden'),
      Field('idregion'),
      Field('telefono'),
      Field('anombre'),
      Field('enfecha', 'datetime'),
      Field('despachador', default=auth.user_id),
      Field('buzon_deshabilitado', 'boolean'),
      Field('confirmacion_entrega'),
      Field.Virtual('days', lambda r: (
          request.now.date() - r.despachado_os.enfecha.date()).days),
      migrate=False)

tabla('despachado',
      Field('folio'),
      Field('grupo'),
      Field('iddt', 'integer'),
      Field('telefono'),
      Field('anombre'),
      Field('enfecha', 'datetime'),
      Field('despachador', default=auth.user_id),
      Field('buzon_deshabilitado', 'boolean'),
      Field('confirmacion_entrega'),
      Field.Virtual('days', lambda r: (
          request.now.date() - r.despachado.enfecha.date()).days),
      migrate=False)

tabla('despachado_tp',
      Field('averia_id'),
      Field('telefono'),
      Field('anombre'),
      Field('enfecha', 'datetime'),
      Field('despachador', default=auth.user_id),
      Field('buzon_deshabilitado', 'boolean'),
      Field('confirmacion_entrega'),
      Field.Virtual('days', lambda r: (
          request.now.date() - r.despachado_tp.enfecha.date()).days),
      migrate=False)

tabla('profile',
      Field('proceso', 'string'),
      Field('ejecutado', 'datetime'),
      Field('tiempo', 'integer'),
      Field('observaciones', 'string'),
      migrate=False)

tabla('provincia',
      Field('provincia', 'string'),
      migrate=False)

tabla('fallo',  # ----------------- no se usa en esta aplicación
      Field('fecha', 'datetime'),
      Field('servicio'),
      Field('tipo'),
      Field('descripcion'),
      migrate=False)

tabla('clave_cierre',
      Field('clave'),
      Field('tipo_clave'),
      Field('descripcion'),
      migrate=False)

tabla('material',
      Field('nombre'),
      Field('tipo'),
      Field('codigo_sap'),
      migrate=False)

tabla('area_automatico_log',
      Field('fecha', 'datetime'),
      Field('automatico', 'boolean'),
      Field('user_id', 'reference auth_user'),
      Field('area_id', 'reference area'),
      migrate=False)

tabla('os',
      Field('fecha', 'datetime'),
      Field('numero_os', 'integer'),
      Field('tipo_os'),
      Field('servicio'),
      Field('clave_cierre'),
      Field('clave_reparador'),
      migrate=False)

tabla('reparada_ra',
      Field('fecha', 'datetime'),
      Field('intervencion'),
      Field('folio'),
      Field('servicio'),
      Field('clave_cierre'),
      Field('clave_reparador'),
      migrate=False)


# faltan: webservice_temp, os_pendiente_temp, mensaje_largo, pendiente_temp
# si hace falta, se migran con fake_migrate=True

""" Relacioness entre tablas """
db.destinatario_grupo.destinatario_id.requires = IS_IN_DB(
    db, 'destinatario.id', ' %(nombre)s %(apellidos)s')
db.destinatario_grupo.grupo_id.requires = IS_IN_DB(
    db, 'grupo.id', ' %(nombre)s - %(descripcion)s')

""" Otras restricciones """
db.destinatario.clave_reparador.requires = [
#     IS_EMPTY_OR(IS_NOT_IN_DB(db, 'destinatario.clave_reparador',
#                 error_message='Ya existe la clave'))
    CLAVE_VALIDATOR(error_message='Ya existe la clave')
]
db.destinatario.telefono.requires = [
    IS_NOT_EMPTY(),
#     IS_INT_IN_RANGE(50000000, 59999999,
#                     error_message='Introduzca un número de teléfono móvil'),
    IS_NOT_IN_DB(db, 'destinatario.telefono', error_message='Ya este número existe')]
db.destinatario.pin.requires = [
#     IS_NOT_EMPTY(),
#     IS_MATCH('\d{4}', error_message='Introduzca un número de 4 dígitos'),
#     IS_NOT_IN_DB(db, 'destinatario.pin', error_message='Ya este pin existe')
    IS_EMPTY_OR(IS_NOT_IN_DB(db, 'destinatario.pin', error_message='Ya existe la clave'))
]
