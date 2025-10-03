# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def user():

    def GET(id=None, **vars):        
        def deletable():
            q = db.asignacion.created_by == id
            q |= db.asignacion.modified_by == id
            q2 = db.asignacion_tp.created_by == id
            q2 |= db.asignacion_tp.modified_by == id
            return not (db(q).count() + db(q2).count())

        def grupos():
            res = db(db.usuario_grupo.usuario_id == id)._select(
                db.usuario_grupo.grupo_id)
            return db(db.grupo.id.belongs(res)).select().as_list()

        def areas():
            res = db(db.usuario_area.usuario_id == id)._select(
                db.usuario_area.area_id)
            return db(db.area.id.belongs(res)).select().as_list()

        def name(user):
            if not user:
                return ''
            return '{first_name} {last_name}'.format(**user).strip()

        if id:
            fields = [
                db.auth_user.id,
                db.auth_user.first_name,
                db.auth_user.last_name,
                db.auth_user.username,
                db.auth_user.registration_key,
                db.auth_user.email,
                db.auth_user.created_by,
                db.auth_user.modified_by,
                db.auth_user.created_on,
                db.auth_user.modified_on
            ]
            user = db(db.auth_user.id == id).select(*fields).first()
            user['name'] = name(user)
            user['grupos'] = grupos()
            user['areas'] = areas()
            user['deletable'] = deletable()
            user['created_by'] = name(db.auth_user(user['created_by']))
            user['modified_by'] = name(db.auth_user(user['modified_by']))
            return response.json(user)
        else:
            from gluon.storage import Storage
            from applications.dar.modules.db.admin import users
            return response.json(users(db, auth, Storage(vars)))

    @Validate.admin
    @Validate.user_in_scope
    def PUT(id, **vars):
        current_values = db(db.auth_user.id == id).select(
            db.auth_user.email,
            db.auth_user.username
        ).first()

        db.auth_user.email.requires = IS_EMPTY_OR(IS_EMAIL())

        # email and username, fails to update with same values due to fields restrictions NOT_IN_DB
        if ('email' in vars) and vars['email'] == current_values.email:
            del vars['email']
        if ('username' in vars) and vars['username'] == current_values.username:
            del vars['username']

        res = db(db.auth_user.id == id).validate_and_update(**vars)
        return response.json(res)

    @Validate.admin
    def POST(*args, **vars):
        # auth.register_bare(**vars), returns a user or False (never errors)
        # This action adds membership 'despachador'
        db.auth_user.password.requires = None  # disable validator
        res = db.auth_user.validate_and_insert(**vars)
        res.id and auth.add_membership(user_id=res.id, role='despachador')
        return response.json(res)

    @Validate.admin
    @Validate.user_in_scope
    @Validate.user_not_referenced
    def DELETE(id, **vars):
        res = db(db.auth_user.id == id).delete()
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def grupos():

    @Validate.admin
    def POST(*args, **vars):
        res = db.usuario_grupo.validate_and_insert(**vars)
        return response.json(res)

    @Validate.admin
    def DELETE(*args, **vars):
        q = db.usuario_grupo.usuario_id == vars['usuario_id']
        q &= db.usuario_grupo.grupo_id == vars['grupo_id']
        db(q).delete()
        return response.json({'deleted': 1, 'errors': {}})

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def areas():

    @Validate.admin
    def POST(*args, **vars):
        res = db.usuario_area.validate_and_insert(**vars)
        return response.json(res)

    @Validate.admin
    def DELETE(*args, **vars):
        q = db.usuario_area.usuario_id == vars['usuario_id']
        q &= db.usuario_area.area_id == vars['area_id']
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
    def user_not_referenced(fn):
        def run(*k, **kw):
            id = k[0]
            q = db.asignacion.created_by == id
            q |= db.asignacion.modified_by == id
            q2 = db.asignacion_tp.created_by == id
            q2 |= db.asignacion_tp.modified_by == id
            if db(q).count() + db(q2).count():
                raise HTTP(
                    405, 'Una regla de integridad impidió realizar esta acción.')
            return fn(*k, **kw)

        return run

    @staticmethod
    def user_in_scope(fn):
        def run(*k, **kw):
            if auth.has_membership('administrador_territorial'):
                id = k[0]
                auth_user_areas = db(db.usuario_area.usuario_id == auth.user_id)._select(
                    db.usuario_area.area_id)
                q = db.usuario_area.area_id.belongs(auth_user_areas)
                q &= db.usuario_area.usuario_id == id
                q2 = db.usuario.created_by == auth.user_id
                c = db(q).count() + db(q2).count()
                if not c:
                    raise HTTP(403, 'Forbidden.')
            return fn(*k, **kw)

        return run
