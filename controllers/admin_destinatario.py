# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def destinatarios():

    def GET(id=None, **vars):
        def deletable(clave_reparador):
            if not clave_reparador:
                return True
            q = db.os.clave_reparador == clave_reparador
            q2 = db.reparada_ra.clave_reparador == clave_reparador
            return not (db(q).count() + db(q2).count())

        def grupos():
            res = db(db.destinatario_grupo.destinatario_id == id)._select(
                db.destinatario_grupo.grupo_id)
            return db(db.grupo.id.belongs(res)).select().as_list()

        def areas():
            res = db(db.destinatario_area.destinatario_id == id)._select(
                db.destinatario_area.area_id)
            return db(db.area.id.belongs(res)).select().as_list()

        def smsgrupos():
            res = db(db.destinatario_smsgrupo.destinatario_id == id)._select(
                db.destinatario_smsgrupo.smsgrupo_id)
            return db(db.smsgrupo.id.belongs(res)).select().as_list()

        def name(user):
            if not user:
                return ''
            return '{first_name} {last_name}'.format(**user).strip()

        if id:
            res = db.destinatario(id).as_dict()
            res['name'] = '{nombre} {apellidos}'.format(**res).strip()
            res['smsgrupos'] = smsgrupos()
            res['grupos'] = grupos()
            res['areas'] = areas()
            res['deletable'] = deletable(res['clave_reparador'])
            res['created_by'] = name(db.auth_user(res['created_by']))
            res['modified_by'] = name(db.auth_user(res['modified_by']))
            return response.json(res)
        else:
            from gluon.storage import Storage
            from applications.dar.modules.db.admin import destinatarios
            return response.json(destinatarios(db, auth, Storage(vars)))

    @Validate.admin
    @Validate.destinatario_in_scope
    @Validate.destinatario_not_referenced
    def DELETE(id, **vars):
        res = db(db.destinatario.id == id).delete()
        return response.json(res)

    @Validate.admin
    @Validate.destinatario_in_scope
    def PUT(id, **vars):
        current_values = db(db.destinatario.id == id).select(
            db.destinatario.telefono,
            db.destinatario.pin,
            db.destinatario.clave_reparador,
        ).first()

        db.destinatario.correo.requires = IS_EMPTY_OR(IS_EMAIL())

        # telefono, pin and clave_reparador, fails to update with same values due to fields restrictions NOT_IN_DB
        if ('telefono' in vars) and vars['telefono'] == current_values.telefono:
            del vars['telefono']
        if ('pin' in vars) and vars['pin'] == current_values.pin:
            del vars['pin']
        if ('clave_reparador' in vars) and vars['clave_reparador'] == current_values.clave_reparador:
            del vars['clave_reparador']

        res = db(db.destinatario.id == id).validate_and_update(**vars)
        return response.json(res)

    @Validate.admin
    def POST(*args, **vars):
        db.destinatario.correo.requires = IS_EMPTY_OR(IS_EMAIL())
        res = db.destinatario.validate_and_insert(**vars)
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def areas():

    @Validate.admin
    def POST(*args, **vars):
        res = db.destinatario_area.validate_and_insert(**vars)
        return response.json(res)

    @Validate.admin
    def DELETE(*args, **vars):
        def end_asignacion(destinatario_id, area_id):
            left = [
                db.central.on((db.asignacion.central_id == db.central.id) &
                              (db.asignacion.region_id == db.central.region_id)),
                db.zona.on(db.asignacion.zona_id == db.zona.id)
            ]
            q = db.asignacion.destinatario_id == destinatario_id
            q &= db.asignacion.termina == None
            q &= ((db.central.area_id == area_id) |
                  (db.zona.area_id == area_id))
            ids = [r.id for r in db(q).select(db.asignacion.id, left=left)]
            db(db.asignacion.id.belongs(ids)).update(termina=request.now)

        def end_asignacion_tp(destinatario_id, area_id):
            q = db.asignacion_tp.zona_id == db.zona_tp.id
            q &= db.zona_tp.area_id == area_id
            q &= db.asignacion_tp.termina == None
            q &= db.asignacion_tp.destinatario_id == destinatario_id
            ids = [r.id for r in db(q).select(db.asignacion_tp.id)]
            db(db.asignacion_tp.id.belongs(ids)).update(termina=request.now)

        q = db.destinatario_area.destinatario_id == vars['destinatario_id']
        q &= db.destinatario_area.area_id == vars['area_id']
        res = db(q).delete()
        if res:
            end_asignacion(vars['destinatario_id'], vars['area_id'])
            end_asignacion_tp(vars['destinatario_id'], vars['area_id'])
        return response.json({'deleted': res, 'erros': {}})

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def smsgrupos():

    @Validate.admin
    def POST(*args, **vars):
        res = db.destinatario_smsgrupo.validate_and_insert(**vars)
        return response.json(res)

    @Validate.admin
    def DELETE(*args, **vars):
        q = db.destinatario_smsgrupo.destinatario_id == vars['destinatario_id']
        q &= db.destinatario_smsgrupo.smsgrupo_id == vars['smsgrupo_id']
        db(q).delete()
        return response.json({'deleted': 1, 'erros': {}})

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def grupos():

    @Validate.admin
    def POST(*args, **vars):
        res = db.destinatario_grupo.validate_and_insert(**vars)
        return response.json(res)

    @Validate.admin
    def DELETE(*args, **vars):
        q = db.destinatario_grupo.destinatario_id == vars['destinatario_id']
        q &= db.destinatario_grupo.grupo_id == vars['grupo_id']
        db(q).delete()
        return response.json({'deleted': 1, 'erros': {}})

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


class Validate:

    @staticmethod
    def admin(fn):
        def run(*k, **kw):
            # Check if login as user (auth_user)
            if auth and auth.user and 'username' in auth.user \
                and (auth.has_membership('administrador') or
                     auth.has_membership('administrador_territorial')):
                return fn(*k, **kw)
            else:
                raise HTTP(403, 'Forbidden.')

        return run

    @staticmethod
    def destinatario_not_referenced(fn):
        def run(*k, **kw):
            id = k[0]
            clave_reparador, destinatario = False, db.destinatario(id)
            if destinatario:
                clave_reparador = destinatario.clave_reparador
            else:
                raise HTTP(405, 'Error de petición.')
            if clave_reparador:
                q = db.os.clave_reparador == clave_reparador
                q2 = db.reparada_ra.clave_reparador == clave_reparador
                if db(q).count() + db(q2).count():
                    raise HTTP(
                        405, 'Una regla de integridad impidió realizar esta acción.')
            return fn(*k, **kw)

        return run

    @staticmethod
    def destinatario_in_scope(fn):
        def run(*k, **kw):
            if auth.has_membership('administrador_territorial'):
                id = k[0]
                auth_user_areas = db(db.usuario_area.usuario_id == auth.user_id)._select(
                    db.usuario_area.area_id)
                q = db.destinatario_area.area_id.belongs(auth_user_areas)
                q &= db.destinatario_area.destinatario_id == id
                q2 = db.destinatario.created_by == auth.user_id
                c = db(q).count() + db(q2).count()
                if not c:
                    raise HTTP(403, 'Forbidden.')
            return fn(*k, **kw)

        return run
