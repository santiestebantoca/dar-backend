# coding: utf8

"""
area_automatico  ** pendientes.php
---
destinatarios ** admin_destinatario.py /destinatarios
destinatario_publica  ** pendientes_tp.php
destinatario_central  ** pendientes.php
destinatario_territorio  ** some php script like (reporte_*.php, 117tosms.php)
destinatario_zona  ** pendientes.php
error_hoy  ** notificación de errores a los administradores (en desarrollo)
repetidos_en_pendiente  **  dashboard /tablas vigiladas / pendiente
---
tppendiente_area ** tp.py /reportes
wspendiente_central ** despachar.php, administrador.py /pendientes, ra.py /reportes
wspendiente_central_despachado buzon.py /reportes_ra /count_ra
tppendiente_area_despachado  buzon.py /reportes_tp /count_tp
---
usuario ** auth.py /users, admin_despachador.py /despachadores for role 'administrador'
area_usuario ** despachador.py /api_area

asignacion_destinatario ** buzon.py /asignaciones
asignacion_tp_destinatario ** buzon.py /asignaciones_tp
---
destinatario_smsgrupo_pendientes ** dar/Stored Procs destinatarios
asignacion_area ** dar/Stored Procs asignaciones
asignacion_tp_area ** dar/Stored Procs asignaciones_tp
area_automatico_log_view ** despachador.py /automatico_log
---
wsordeneserv_central ** ra.py /ordenes
"""

tabla('destinatarios',
      Field('nombre'),
      Field('clave'),
      Field('telefono'),
      Field('pin'),
      Field('activo', 'boolean'),
      Field('created_by', 'integer'),
      migrate=False)

tabla('wsordeneserv_central',
      Field('creado'),
      Field('servicio'),
      Field('orden'),
      #   Field('fechaso'),
      #   Field('horaso'),
      Field('fechasr'),
      Field('fechar'),
      Field('fechaor'),
      Field('fechaa'),
      #   Field('fechaocu'),
      #   Field('fechaok'),
      Field('idplantas'),
      Field('idregion'),
      #   Field('tiposerv'),
      Field('clavemov'),
      #   Field('categcli'),
      Field('oficina'),
      Field('estado'),
      Field('nombre'),
      Field('entre'),
      Field('observacion'),
      Field('ruta'),
      Field('nombpta'),
      Field('area_id'),
      Field('despachado'),
      Field('cl'),
      Field('wan'),
      Field('lan'),
      Field('puerta'),
      Field('velocidad'),
      Field('idorden'),
      Field('asociado'),
      primarykey=['idorden', 'idregion'],
      migrate=False)

tabla('wspendiente_central',
      Field('creado'),
      Field('folio', type='id'),
      Field('grupo'),
      Field('descgrupo'),
      Field('centro'),
      Field('telefono'),
      Field('nombre'),
      Field('direccion'),
      Field('demorat'),
      Field('cableP'),
      Field('parP'),
      Field('direcciontP'),
      Field('terminalP'),
      Field('cableS'),
      Field('parS'),
      Field('terminalS'),
      Field('direcciontS'),
      Field('cl'),
      Field('problema'),
      Field('idplantas'),
      Field('nombpta'),
      Field('iddt', 'integer'),
      Field('zona'),
      Field('region'),
      Field('observacion'),
      Field('telfloca'),
      Field('inicio'),
      Field('fin'),
      Field('prueba'),
      Field('clave'),
      Field('tiposerv'),
      Field('area_id'),
      Field('despachado', 'integer'),
      Field('equipo'),
      primarykey=['folio', 'iddt'],
      migrate=False)

tabla('repetidos_en_pendiente',  # () => registros repetidos (según: creado, folio, grupo, idplantas, idcentel, iddt)
      Field('folio'),
      migrate=False)

tabla('tppendiente_area',
      Field('id'),
      Field('creado'),
      Field('identificativo'),
      Field('numero_telefonico'),
      Field('modelo'),
      Field('fabricante'),
      Field('gestionado', 'boolean'),
      Field('categoria'),
      Field('cerradura'),
      Field('codigos_de_alarma'),
      Field('estados_pendientes'),
      Field('piezas'),
      Field('fuente_de_alarma'),
      Field('tiempo', 'integer'),
      Field('zona'),
      Field('direccion'),
      Field('otros_datos'),
      Field('localidad'),
      Field('ct'),
      Field('dt'),
      Field('soporte'),
      Field('fecha_averia_sigetp', 'datetime'),
      Field('id_ct', 'integer'),
      Field('area_id', 'integer'),
      Field('despachado', 'integer'),
      migrate=False)

tabla('usuario',
      Field('name'),
      Field('username'),
      Field('registration_key'),
      Field('created_by', 'reference auth_user'),
      Field('auth_group_1', 'integer'),
      Field('auth_group_2', 'integer'),
      Field('auth_group_3', 'integer'),
      migrate=False)

tabla('area_usuario',
      Field('nombre'),
      Field('territorio_id', 'integer'),
      Field('territorio_nombre'),
      Field('territorio_orden', 'integer'),
      Field('automatico', 'boolean'),
      Field('usuario_id', 'integer'),
      migrate=False)

tabla('asignacion_destinatario',
      Field('destinatario_id'),
      Field('territorio'),
      Field('area'),
      Field('zona'),
      Field('central'),
      migrate=False)

tabla('asignacion_tp_destinatario',
      Field('destinatario_id'),
      Field('territorio'),
      Field('area'),
      Field('zona'),
      migrate=False)

tabla('area_automatico_log_view',
      Field('fecha', 'datetime'),
      Field('automatico'),
      Field('user_id', 'integer'),
      Field('area_id', 'integer'),
      Field('area'),
      Field('username'),
      Field('usuario'),
      migrate=False)

tabla('wspendiente_central_despachado',  # (area_id) => registros de pendientes de un área (central tiene area_id)
      Field('creado'),
      Field('folio'),
      Field('grupo'),
      Field('descgrupo'),
      Field('centro'),
      Field('telefono'),
      Field('nombre'),
      Field('direccion'),
      Field('demorat'),
      Field('cableP'),
      Field('parP'),
      Field('direcciontP'),
      Field('terminalP'),
      Field('cableS'),
      Field('parS'),
      Field('terminalS'),
      Field('direcciontS'),
      Field('cl'),
      Field('problema'),
      Field('idplantas'),
      Field('nombpta'),
      Field('iddt', 'integer'),
      Field('zona'),
      Field('region'),
      Field('observacion'),
      Field('telfloca'),
      Field('inicio'),
      Field('fin'),
      Field('prueba'),
      Field('tiposerv'),      
      Field('area_id'),
      Field('anombre'),
      Field('atelefono'),
      Field('despachador'),
      Field('enfecha'),
      Field('buzon_deshabilitado', 'boolean'),
      primarykey=['folio', 'iddt'],
      migrate=False)

tabla('tppendiente_area_despachado',
      Field('id'),
      Field('creado'),
      Field('identificativo'),
      Field('numero_telefonico'),
      Field('modelo'),
      Field('fabricante'),
      Field('gestionado', 'boolean'),
      Field('categoria'),
      Field('cerradura'),
      Field('codigos_de_alarma'),
      Field('estados_pendientes'),
      Field('piezas'),
      Field('fuente_de_alarma'),
      Field('tiempo', 'integer'),
      Field('zona'),
      Field('direccion'),
      Field('otros_datos'),
      Field('localidad'),
      Field('ct'),
      Field('dt'),
      Field('soporte'),
      Field('fecha_averia_sigetp', 'datetime'),
      Field('id_ct', 'integer'),
      Field('area_id', 'integer'),
      Field('anombre'),
      Field('atelefono'),
      Field('despachador'),
      Field('enfecha', 'datetime'),
      Field('buzon_deshabilitado', 'boolean'),
      migrate=False)
