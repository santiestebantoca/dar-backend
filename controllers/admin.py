# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def areas_administradas():

    def GET(*args, **vars):
        if auth.has_membership('administrador'):
            res = db(db.area).select(
                db.area.id,
                db.area.nombre,
                db.area.territorio_id
            )
        elif auth.has_membership('administrador_territorial'):
            res = db(db.area_usuario.usuario_id == auth.user_id).select(
                db.area_usuario.id,
                db.area_usuario.nombre,
                db.area_usuario.territorio_id
            )
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def territorios_administrados():

    def GET(*args, **vars):
        if auth.has_membership('administrador'):
            res = db(db.territorio).select(
                db.territorio.id,
                db.territorio.nombre,
            )
        elif auth.has_membership('administrador_territorial'):
            _areas = db(db.area_usuario.usuario_id == auth.user_id)._select(
                db.area_usuario.territorio_id)
            res = db(db.territorio.id.belongs(_areas)).select(
                db.territorio.id,
                db.territorio.nombre,
            )
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def grupos():

    def GET(*args, **vars):
        return response.json(db(db.grupo).select())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def smsgrupos():

    def GET(*args, **vars):
        return response.json(db(db.smsgrupo).select())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def authgroup():

    def GET(*args, **vars):
        return response.json(db(db.auth_group).select())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
