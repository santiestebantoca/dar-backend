# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def zonas():

    def GET(id=None, **vars):

        if id:
            def name(user):
                if not user:
                    return ''
                return '{first_name} {last_name}'.format(**user).strip()
                
            res = db.zona(id).as_dict()
            res['area'] = db.area(res['area_id'])
            res['area']['territorio'] = db.territorio(res['area']['territorio_id']).nombre
            res['created_by'] = name(db.auth_user(res['created_by']))
            res['modified_by'] = name(db.auth_user(res['modified_by']))
            return response.json(res)
        else:
            from gluon.storage import Storage
            from applications.dar.modules.db.admin import zonas
            return response.json(zonas(db, auth, Storage(vars)))

    @Validate.admin
    @Validate.zona_in_scope
    def DELETE(id, **vars):
        res = db(db.zona.id == id).delete()
        return response.json(res)

    @Validate.admin
    @Validate.zona_in_scope
    def PUT(id, **vars):
        res = db(db.zona.id == id).validate_and_update(**vars)
        return response.json(res)

    @Validate.admin
    @Validate.area_in_scope
    def POST(*args, **vars):
        res = db.zona.validate_and_insert(**vars)
        return response.json(res)

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
    def area_in_scope(fn):
        def run(*k, **kw):
            if auth.has_membership('administrador_territorial'):
                area_id = kw['area_id']
                q = db.usuario_area.area_id == area_id
                q &= db.usuario_area.usuario_id == auth.user_id
                if not db(q).count():
                    raise HTTP(403, 'Forbidden.')
            return fn(*k, **kw)

        return run

    @staticmethod
    def zona_in_scope(fn):
        def run(*k, **kw):
            if auth.has_membership('administrador_territorial'):
                id = k[0]
                q = db.usuario_area.area_id == db.zona.area_id
                q &= db.zona.id == id
                q &= db.usuario_area.usuario_id == auth.user_id
                if not db(q).count():
                    raise HTTP(403, 'Forbidden.')
            return fn(*k, **kw)

        return run
