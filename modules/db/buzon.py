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
        db.wspendiente_central_despachado.folio,
        db.wspendiente_central_despachado.telefono,
        db.wspendiente_central_despachado.nombre,
        db.wspendiente_central_despachado.direccion,
        db.wspendiente_central_despachado.cl,
        db.wspendiente_central_despachado.cableP,
        db.wspendiente_central_despachado.parP,
        db.wspendiente_central_despachado.terminalP,
        db.wspendiente_central_despachado.direcciontP,
        db.wspendiente_central_despachado.cableS,
        db.wspendiente_central_despachado.parS,
        db.wspendiente_central_despachado.terminalS,
        db.wspendiente_central_despachado.direcciontS,
        db.wspendiente_central_despachado.inicio,
        db.wspendiente_central_despachado.fin,
        db.wspendiente_central_despachado.problema,
        db.wspendiente_central_despachado.prueba,
        db.wspendiente_central_despachado.grupo,
        db.wspendiente_central_despachado.demorat,
        db.wspendiente_central_despachado.observacion,
        db.wspendiente_central_despachado.telfloca,
    ]
    args = dict(distinct=True)  # , orderby=~db.wspendiente_central_despachado.folio)
    vars.limit and args.update(limitby=limitby(vars))
    if vars.atelefono:
        q = db.wspendiente_central_despachado.atelefono == vars.atelefono
    else:
        q = db.wspendiente_central_despachado.atelefono == auth.user.telefono
    # q &= db.wspendiente_central_despachado.buzon_deshabilitado != True
    # return::
    sql = db(q)._select(*fds, left=left, **args)
    rows = db.executesql(sql)
    sql = db(q)._select(*fds, left=left).split(' FROM ', 1)
    sql = 'SELECT COUNT(DISTINCT wspendiente_central_despachado.folio) FROM ' + sql[1]
    count = db.executesql(sql)[0][0]
    return dict(data=rows, total=count)


def reportes_tp(db, auth, vars):
    """
    returns::
    """
    left = False
    fds = [
        db.tppendiente_area_despachado.id,
        db.tppendiente_area_despachado.identificativo,
        db.tppendiente_area_despachado.numero_telefonico,
        db.tppendiente_area_despachado.modelo,
        db.tppendiente_area_despachado.categoria,
        db.tppendiente_area_despachado.cerradura,
        db.tppendiente_area_despachado.codigos_de_alarma,
        db.tppendiente_area_despachado.estados_pendientes,
        db.tppendiente_area_despachado.tiempo,
        db.tppendiente_area_despachado.direccion,
        db.tppendiente_area_despachado.soporte,
        db.tppendiente_area_despachado.fecha_averia_sigetp
    ]
    args = dict(distinct=True)  # , orderby=~db.tppendiente_area_despachado.id)
    vars.limit and args.update(limitby=limitby(vars))
    if vars.atelefono:
        q = db.tppendiente_area_despachado.atelefono == vars.atelefono
    else:
        q = db.tppendiente_area_despachado.atelefono == auth.user.telefono
    # q &= db.tppendiente_area_despachado.buzon_deshabilitado != True
    # return::
    sql = db(q)._select(*fds, left=left, **args)
    rows = db.executesql(sql)
    sql = db(q)._select(*fds, left=left).split(' FROM ', 1)
    sql = 'SELECT COUNT(DISTINCT tppendiente_area_despachado.id) FROM ' + sql[1]
    count = db.executesql(sql)[0][0]
    return dict(data=rows, total=count)
