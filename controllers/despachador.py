# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


"""
DAR Model:
territorio: PK (id[SIPREC]), FK (provincia, region)
area (not in SIPREC model): PK (id), FK (territorio)
grupo: PK (id)
smsgrupo: PK (id)
destinatario: PK (id)
destinatario_area: PK (id), FK (destinatario, area)
destinatario_grupo: PK (id), FK (destinatario, grupo)
destinatario_smsgrupo: PK (id), FK (destinatario, smsgrupo)
usuario_area: PK (id), FK (auth_user, area)
usuario_grupo: PK (id), FK (auth_user, grupo)  // user membership 'despachador'

(v) area_usuario  // select by 'user', data from area & territorio
-> usuario_area
-> area
-> territorio

(sp) grupos  // select by 'user', data from grupo
-> grupo
-> usuario_grupo

(sp) destinatarios // select by 'area' & 'user', data from destinatario & grupo
-> (v) destinatario_smsgrupo_pendientes  // destinatario(smsgrupo pendiente) & area
-> destinatario_grupo
-> grupo
-> usuario_grupo  // select by 'user', valid 'grupo' for 'destinatario'
"""


@request.restful()
def area_automatico_log():

    def GET(area_id):
        """
        :return: last 10 `area`.`automatico` updates
        """
        ds = db(db.area_automatico_log_view.area_id == area_id)
        return response.json(ds.select(
            orderby=~db.area_automatico_log_view.id,
            limitby=(0, 10),
        ))

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def areas():

    @auth.requires_membership('despachador')
    def GET(id=None):
        """
        :return: areas related to the authenticated user
        """
        if id:
            res = db(db.area_usuario.id == id).select()
        else:
            fds = [
                db.area_usuario.id,
                db.area_usuario.nombre,
                db.area_usuario.automatico,
                db.area_usuario.territorio_id,
                db.area_usuario.territorio_nombre,
                db.area_usuario.territorio_orden,
                # db.area_usuario.usuario_id,
            ]
            res = db.executesql(db(db.area_usuario.usuario_id == auth.user_id)._select(*fds))
        return response.json(res)

    @auth.requires_membership('despachador')
    @Validate.area_in_scope
    def PUT(id, **vars):
        res = db(db.area.id == id).validate_and_update(**vars)
        if res:
            db.area_automatico_log.insert(
                area_id=id,
                user_id=auth.user_id,
                automatico=vars['automatico']
            )
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def grupos():

    # @auth.requires_membership('despachador')
    def GET(*args, **vars):
        usuario = auth.user_id
        res = db.executesql('call grupos({})'.format(usuario))
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def destinatarios():

    @auth.requires_membership('despachador')
    def GET(*args, **vars):
        area = vars['area_id']
        usuario = auth.user_id
        res = db.executesql('call destinatarios({}, {})'.format(area, usuario))
        return response.json(res)

    @auth.requires_membership('despachador')
    @Validate.destinatario_in_scope
    def PUT(id, **vars):
        res = db(db.destinatario.id == id).validate_and_update(**vars)
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def sms():

    def POST(*args, **vars):
        """
        $number = $_POST['number'];
        $text = $_POST['text'];
        $sender = $_POST['sender'];
        API
        return:: (String) number of affected rows {0, 1}
        """
        from urllib.request import urlopen
        from urllib.parse import urlencode
        url = myconf.get('api_sms.enviar')
        data = dict(number=vars['telefono'], text=vars['message'], sender='DAR-INFORMA')
        data = urlencode(data).encode()  # to binary
        res = urlopen(url, data).read().decode()  # to str
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


class Validate:

    @staticmethod
    def area_in_scope(fn):
        def run(*k, **kw):
            area_id = k[0]
            q = db.usuario_area.usuario_id == auth.user_id
            q &= db.usuario_area.area_id == area_id
            if db(q).isempty():
                raise HTTP(403, 'Forbidden.')
            return fn(*k, **kw)

        return run

    @staticmethod
    def destinatario_in_scope(fn):
        def run(*k, **kw):
            q = db.usuario_area.usuario_id == auth.user_id
            auth_user_areas = db(q)._select(db.usuario_area.area_id)
            destinatario_id = k[0]
            q = db.destinatario_area.destinatario_id == destinatario_id
            q &= db.destinatario_area.area_id.belongs(auth_user_areas)
            if db(q).isempty():
                raise HTTP(403, 'Forbidden.')
            return fn(*k, **kw)

        return run
