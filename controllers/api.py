# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def despachado_tp():
    """
    This API is used by Malagón
    """
    def GET(*args, **vars):
        """
        'desde' & 'hasta', represent a date in the format YYYY-MM-DD (HTML date format)
        """
        if ('desde' in vars) or ('hasta' in vars):
            from datetime import datetime, timedelta
        q = db.despachado_tp.id > 0
        if 'averia_id' in vars:
            q &= db.despachado_tp.averia_id == vars['averia_id']
        if 'desde' in vars:
            q &= db.despachado_tp.enfecha > vars['desde']
        if 'hasta' in vars:
            hasta = datetime.strptime(vars['hasta'], '%Y-%m-%d') + timedelta(days=1)
            q &= db.despachado_tp.enfecha < hasta
        return response.json(db(q).select())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def pendiente_tp():
    """
    This API is used by Malagón
    """
    def GET(*args, **vars):

        sql = """
          SELECT
            tppendiente.id,
            tppendiente.identificativo,
            tppendiente.numero_telefonico,
            tppendiente.modelo,
            tppendiente.fabricante,
            tppendiente.gestionado,
            tppendiente.categoria,
            tppendiente.cerradura,
            tppendiente.codigos_de_alarma,
            tppendiente.estados_pendientes,
            tppendiente.piezas,
            tppendiente.fuente_de_alarma,
            tppendiente.tiempo,
            tppendiente.zona,
            tppendiente.direccion,
            tppendiente.otros_datos,
            tppendiente.localidad,
            tppendiente.ct,
            tppendiente.dt,
            tppendiente.soporte,
            tppendiente.fecha_averia_sigetp,
            tppendiente.id_ct 
          FROM tppendiente
            INNER JOIN tpupdate ON (tppendiente.creado = tpupdate.fecha)"""
        return response.json(db.executesql(sql))

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
