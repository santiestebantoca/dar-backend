# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def reportes():

    @auth.requires_login()
    def GET(id=None, **vars):
        if id:
            pass
        else:
            from gluon.storage import Storage
            from applications.dar.modules.db.buzon import reportes_ra
            return response.json(reportes_ra(db, auth, Storage(vars)))

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def cierre():
    """
    Remote API (that uses SIPREC Web Service)
    params::
        folio, clave_cierre, clave_reparador, caller
    return::
        ws                                     
        ---------------------------------------
        Clave Cierre, No Existe
        Folio No Existe o No ha sido Asignado
        Clave Operador, No Existe
        CIERRE PARCIAL
        CIERRE TOTAL

        ** On remote API error, the reponse is an large html 
    """
    @auth.requires_login()
    def POST(*args, **vars):
        from urllib.request import urlopen
        from urllib.parse import urlencode
        vars['clave_reparador'] = auth.user.clave_reparador
        vars['caller'] = auth.user.telefono
        try:
            url = myconf.get('api_ra_reportes.cerrar')
            data_encode = urlencode(vars).encode()  # to binary
            with urlopen(url, data_encode) as res:  # using POST method
                msg = res.read().decode()  # to str
                message = msg.strip() if len(msg) < 40 else 'Error no especificado'
                accepted = message in ['CIERRE TOTAL', 'CIERRE PARCIAL']
        except:
            message = 'Error de conexión con la API'
            accepted = False
        return response.json({'accepted':accepted, 'message':message})

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
