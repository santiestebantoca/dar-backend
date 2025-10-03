# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


def limitby(vars):
    min, max = vars.limit.split(',')
    return (int(min), int(max))


def auth_user_areas(db, auth):
    return db(db.usuario_area.usuario_id == auth.user_id)._select(db.usuario_area.area_id)


def users(db, auth, vars):
    """
    returns::
    id > 1 because 1 is `sistema`
    (admin): all rows from `usuario`
    (admin_terr): rows from `usuario` where
        (`usuario` shares `area` with auth.user) or \
        ((`usuario` has no area) and (`usuario` is created by auth.user))
    """
    left = False
    fds = [db.usuario.id, db.usuario.name, db.usuario.registration_key]
    args = dict(distinct=True, orderby=~db.usuario.id)
    vars.limit and args.update(limitby=limitby(vars))
    q = db.usuario.id > 1
    if vars.name:
        q &= db.usuario.name.contains(vars.name)
    if vars.no_area:
        left = db.usuario_area.on(db.usuario_area.usuario_id == db.usuario.id)
        q &= db.usuario_area.id == None
    elif vars.area:
        q &= db.usuario.id == db.usuario_area.usuario_id
        q &= db.usuario_area.area_id == vars.area
    elif vars.territorio:
        q &= db.usuario.id == db.usuario_area.usuario_id
        q &= db.usuario_area.area_id == db.area.id
        q &= db.area.territorio_id == vars.territorio
    if vars.blocked:
        q &= db.usuario.registration_key == 'blocked'
    if vars.group:
        q &= db.usuario.id == db.auth_membership.user_id
        q &= db.auth_membership.group_id == vars.group
    # administrador_territorial::
    if auth.has_membership('administrador_territorial'):
        left = db.usuario_area.on(db.usuario_area.usuario_id == db.usuario.id)
        q &= db.usuario_area.area_id.belongs(auth_user_areas(db, auth))
        q |= (db.usuario_area.id == None) & \
            (db.usuario.created_by == auth.user_id)
    # return::
    sql = db(q)._select(*fds, left=left, **args)
    rows = db.executesql(sql)
    sql = db(q)._select(*fds, left=left).split(' FROM ', 1)
    sql = 'SELECT COUNT(DISTINCT usuario.id) FROM ' + sql[1]
    count = db.executesql(sql)[0][0]
    return dict(data=rows, total=count)


def destinatarios(db, auth, vars):
    """
    returns::
    (admin): all rows from `destinatarios`
    (admin_terr): rows from `destinatarios` where
        (`destinatarios` shares `area` with auth.user) or \
        ((`destinatarios` has no area) and (`destinatarios` is created by auth.user))
    """
    left = False
    fds = [db.destinatarios.id, db.destinatarios.nombre, db.destinatarios.activo]
    args = dict(distinct=True, orderby=~db.destinatarios.id)
    vars.limit and args.update(limitby=limitby(vars))
    q = db.destinatarios.id > 0
    if vars.nombre:
        q &= db.destinatarios.nombre.contains(vars.nombre)
    if vars.clave:
        q &= db.destinatarios.clave.contains(vars.clave)
    if vars.pin:
        q &= db.destinatarios.pin.contains(vars.pin)
    if vars.telefono:
        q &= db.destinatarios.telefono.contains(vars.telefono)
    if vars.no_activo:
        q &= db.destinatarios.activo == False
    if vars.no_area:
        left = db.destinatario_area.on(
            db.destinatario_area.destinatario_id == db.destinatarios.id)
        q &= db.destinatario_area.id == None
        if auth.has_membership('administrador_territorial'):
            q &= db.destinatario.created_by == auth.user_id
    elif vars.area:
        q &= db.destinatarios.id == db.destinatario_area.destinatario_id
        q &= db.destinatario_area.area_id == vars.area
    elif vars.territorio:
        q &= db.destinatarios.id == db.destinatario_area.destinatario_id
        q &= db.destinatario_area.area_id == db.area.id
        q &= db.area.territorio_id == vars.territorio
    if vars.smsgrupo:
        q &= db.destinatarios.id == db.destinatario_smsgrupo.destinatario_id
        q &= db.destinatario_smsgrupo.smsgrupo_id == vars.smsgrupo
    if vars.grupo:
        q &= db.destinatarios.id == db.destinatario_grupo.destinatario_id
        q &= db.destinatario_grupo.grupo_id == vars.grupo
    # administrador_territorial::
    if auth.has_membership('administrador_territorial'):
        left = db.destinatario_area.on(
            db.destinatario_area.destinatario_id == db.destinatarios.id)
        q &= db.destinatario_area.area_id.belongs(auth_user_areas(db, auth))
        q |= (db.destinatario_area.id == None) & \
            (db.destinatarios.created_by == auth.user_id)
    # return::
    sql = db(q)._select(*fds, left=left, **args)
    rows = db.executesql(sql)
    sql = db(q)._select(*fds, left=left).split(' FROM ', 1)
    sql = 'SELECT COUNT(DISTINCT destinatarios.id) FROM ' + sql[1]
    count = db.executesql(sql)[0][0]
    return dict(data=rows, total=count)


def zonas(db, auth, vars):
    """
    returns::
    (admin): all rows from `zonas`
    (admin_terr): rows from `zonas` where
        (`zona` shares `area` with auth.user)
    """
    fds = [db.zona.id, db.zona.nombre, db.zona.descripcion]
    args = dict(orderby=~db.zona.id)
    vars.limit and args.update(limitby=limitby(vars))
    q = db.zona.id > 0
    if vars.nombre:
        q &= db.zona.nombre.contains(vars.nombre)
    if vars.descripcion:
        q &= db.zona.descripcion.contains(vars.descripcion)
    if vars.area:
        q &= db.zona.area_id == vars.area
    elif vars.territorio:
        q &= db.zona.area_id == db.area.id
        q &= db.area.territorio_id == vars.territorio
    # administrador_territorial::
    if auth.has_membership('administrador_territorial'):
        q &= db.zona.area_id.belongs(auth_user_areas(db, auth))
    # return::
    sql = db(q)._select(*fds, **args)
    rows = db.executesql(sql)
    sql = db(q)._select(*fds).split(' FROM ', 1)
    sql = 'SELECT COUNT(DISTINCT zona.id) FROM ' + sql[1]
    count = db.executesql(sql)[0][0]
    return dict(data=rows, total=count)
