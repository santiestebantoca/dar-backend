# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def pending():

    @auth.requires_login()
    def GET(*args, **vars):
        atelefono = vars.get('atelefono', auth.user.telefono)
        ra = db(
            (db.wspendiente_central_despachado.atelefono == atelefono) &
            (db.wspendiente_central_despachado.buzon_deshabilitado != True)
        ).count(distinct=db.wspendiente_central_despachado.folio)
        tp = db(
            (db.tppendiente_area_despachado.atelefono == atelefono) &
            (db.tppendiente_area_despachado.buzon_deshabilitado != True)
        ).count(distinct=db.tppendiente_area_despachado.id)
        return response.json(dict(ra=ra, tp=tp))

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def asignaciones():

    @auth.requires_login()
    def GET(*args, **vars):
        destinatario_id = vars.get('destinatario_id', auth.user.id)
        ra = db(db.asignacion_destinatario.destinatario_id == destinatario_id).select(
            db.asignacion_destinatario.territorio,
            db.asignacion_destinatario.area,
            db.asignacion_destinatario.zona,
            db.asignacion_destinatario.central,
        )
        tp = db(db.asignacion_tp_destinatario.destinatario_id == destinatario_id).select(
            db.asignacion_tp_destinatario.territorio,
            db.asignacion_tp_destinatario.area,
            db.asignacion_tp_destinatario.zona,
        )
        return response.json(dict(ra=ra, tp=tp))

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def claves():

    @auth.requires_login()
    def GET(*args, **vars):
        res = db.executesql(db(db.clave_cierre)._select())
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def materiales():

    @auth.requires_login()
    def GET(*args, **vars):
        res = db(db.material).select()
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
