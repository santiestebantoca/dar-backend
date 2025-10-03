# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


def limitby(vars):
    min, max = vars.limit.split(',')
    return (int(min), int(max))


def reportes_ra(db, auth, vars):
    """
    returns::
    """
    left = False
    fds = [
        db.wspendiente_central.folio,
        db.wspendiente_central.telefono,
        db.wspendiente_central.nombre,
        db.wspendiente_central.direccion,
        db.wspendiente_central.cl,
        db.wspendiente_central.cableP,
        db.wspendiente_central.parP,
        db.wspendiente_central.terminalP,
        db.wspendiente_central.direcciontP,
        db.wspendiente_central.cableS,
        db.wspendiente_central.parS,
        db.wspendiente_central.terminalS,
        db.wspendiente_central.direcciontS,
        db.wspendiente_central.inicio,
        db.wspendiente_central.fin,
        db.wspendiente_central.problema,
        db.wspendiente_central.prueba,
        db.wspendiente_central.grupo,
        db.wspendiente_central.demorat,
        db.wspendiente_central.observacion,
        db.wspendiente_central.telfloca,
        db.wspendiente_central.nombpta,
        db.wspendiente_central.iddt,
        db.wspendiente_central.zona,
        db.wspendiente_central.clave,
        db.wspendiente_central.tiposerv,
        db.wspendiente_central.despachado
    ]
    args = dict(distinct=True)  # , orderby=~db.wspendiente_central.folio)
    vars.limit and args.update(limitby=limitby(vars))
    q = db.wspendiente_central.folio == 0
    if vars.area_id:
        q = db.wspendiente_central.area_id == vars.area_id
    # return::
    sql = db(q)._select(*fds, left=left, **args)
    rows = db.executesql(sql)
    sql = db(q)._select(*fds, left=left).split(' FROM ', 1)
    sql = 'SELECT COUNT(DISTINCT wspendiente_central.folio) FROM ' + sql[1]
    count = db.executesql(sql)[0][0]
    return dict(data=rows, total=count)


def reportes_tp(db, auth, vars):
    """
    returns::
    """
    left = False
    fds = [
        db.tppendiente_area.id,
        db.tppendiente_area.identificativo,
        db.tppendiente_area.numero_telefonico,
        db.tppendiente_area.modelo,
        db.tppendiente_area.categoria,
        db.tppendiente_area.cerradura,
        db.tppendiente_area.codigos_de_alarma,
        db.tppendiente_area.estados_pendientes,
        db.tppendiente_area.tiempo,
        db.tppendiente_area.direccion,
        db.tppendiente_area.soporte,
        db.tppendiente_area.fecha_averia_sigetp,
        db.tppendiente_area.zona,
        db.tppendiente_area.piezas,
        db.tppendiente_area.despachado,
    ]
    args = dict(distinct=True)  # , orderby=~db.tppendiente_area.id)
    vars.limit and args.update(limitby=limitby(vars))
    q = db.tppendiente_area.id == 0
    if vars.area_id:
        q = db.tppendiente_area.area_id == vars.area_id
    # return::
    sql = db(q)._select(*fds, left=left, **args)
    rows = db.executesql(sql)
    sql = db(q)._select(*fds, left=left).split(' FROM ', 1)
    sql = 'SELECT COUNT(DISTINCT tppendiente_area.id) FROM ' + sql[1]
    count = db.executesql(sql)[0][0]
    return dict(data=rows, total=count)
