# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def login():
    def GET():
        return response.json(user())

    def POST(**vars):
        if vars['destinatario']:
            login_bare_destinatario(vars['username'], vars['password'])
        else:
            login_bare(vars['username'], vars['password'])
        return response.json(user())

    def DELETE():
        if auth.user:
            log = auth.messages['logout_log']
            origin = 'auth' if 'username' in auth.user else 'auth_dest'
            auth.log_event(log, auth.user, origin=origin)
            auth.logout_bare()
        return response.json(user())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


def user():
    if auth.user:
        if 'username' in auth.user:
            return dict(
                id=auth.user_id,
                name='{first_name} {last_name}'.format(**auth.user).strip(),
                username=auth.user.username,
                email=auth.user.email,
                despachador=auth.has_membership('despachador'),
                admin=auth.has_membership('administrador'),
                admin_territorial=auth.has_membership(
                    'administrador_territorial'),
                user_groups=auth.user_groups,
                is_impersonating=auth.is_impersonating(),
                can_impersonate=can_impersonate(),
            )
        else:
            clave = auth.user.clave_reparador if 'clave_reparador' in auth.user else ''
            return dict(
                id=auth.user.id,
                name='{nombre} {apellidos}'.format(**auth.user).strip(),
                telefono=auth.user.telefono,
                correo=auth.user.correo,
                activo=auth.user.activo,
                clave=clave,
                destinatario=True
            )
    return auth.user


def login_bare_destinatario(username, password):
    if username.isnumeric() and password.isnumeric():
        user = db.destinatario(telefono=username)
        if user and request.is_local:
            auth.login_user(user)
            return user
        if user:
            if password == str(user['pin']):
                q = db.destinatario_smsgrupo.destinatario_id == user['id']
                q &= db.destinatario_smsgrupo.smsgrupo_id == 1
                if db(q).count():
                    auth.login_user(user)
                    auth.log_event(
                        auth.messages['login_log'], user, origin='auth_dest')
                    return user
    return False


def login_bare(username, password):
    """
    A version of Auth.login_bare from gluon.tools customized for this app
    In this version, user must be in database to login
    Differences:
    No auth login method / No password validation for local request
    """
    def let(user):
        auth.login_user(user)
        auth.log_event(auth.messages['login_log'], user)
        return user

    user = db.auth_user(username=username)
    if user:
        if request.is_local:
            return let(user)
        for login_method in auth.settings.login_methods:
            if login_method != auth and login_method(username, password):
                if (user.registration_key is None
                        or not user.registration_key.strip()):
                    return let(user)
    message = 'Login failed with credentials %(username)s; %(password)s'
    args = dict(username=username, password=password)
    auth.log_event(message % args)
    return False


@request.restful()
def impersonate():
    def POST(*args, **vars):
        if can_impersonate():
            auth.impersonate(request.args(0) or '0')
        else:
            auth.impersonate('0')
        return response.json(user())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def users():
    def GET(*args, **vars):
        if 'name' in vars:
            q = db.usuario.name.contains(vars['name'])
            res = db(q).select(limitby=(0, 10))
        else:
            res = db(db.usuario).select()
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


def can_impersonate():
    return auth.user and 'username' in auth.user and auth.has_membership('administrador')
