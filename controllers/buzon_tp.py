# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def reportes():
    """
    Like in tp/reportes but filtering by 'atelefono'
    """
    @auth.requires_login()
    def GET(id=None, **vars):
        if id:
            pass
        else:
            from gluon.storage import Storage
            from applications.dar.modules.db.buzon import reportes_tp
            return response.json(reportes_tp(db, auth, Storage(vars)))

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def reporte():
    @auth.requires_login()
    def GET(id=None, **vars):
        """
        If `id` doesn't exist it returns:: HTTP 400 Bad Request
        """
        from urllib.request import urlopen
        import ssl
        from json import load
        context = ssl._create_unverified_context()
        url = myconf.get('api_tp.operaciones') + '/' + id + '/'
        try:
            with urlopen(url, context=context) as res:
                data = load(res)
        except: 
            data = {}
        return response.json(data)
    
    @auth.requires_login()
    def PUT(id=None, **vars):
        from urllib.request import urlopen, Request
        import ssl
        from json import load
        context = ssl._create_unverified_context()
        url = myconf.get('api_tp.operaciones') + '/' + id + '/'
        req = Request(url, method='PUT')
        with urlopen(req, context=context) as res:
            data = load(res)
        return response.json(data)
    
    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def options():
    @auth.requires_login()
    def GET(id=None, **vars):
        """
        Remote API returns (json)::
        {
            name, description, parses,
            actions: {
                PUT: {
                    ...,
                    estados: {..., type, label, choices: [...]}, // Show in `Pendiente` UI
                    mantenimiento: {..., type, label, choices: [...]}, // Show in `Mantenimiento` UI
                    clave_trabajador: {..., choices: [
                        {display_name: 'AH0001', value: '1529' },
                        ...
                        ]
                    }, // Backend logic from login user
                    cierre: {..., type: boolean}, // Frontend logic from `averia`.`borrado_de_alarma` 
                    piezas_pendientes: {..., type, label, choices: [...]} // Show in `Pendiente` UI
                    piezas_cierre: {..., type, label, choices: [...]} // Show in `Cierre` UI
                    piezas_mtto: {..., type, label, choices: [...]} // Show in `Mtto` UI
                }
            }
        }
        """
        from urllib.request import urlopen, Request
        import ssl
        from json import load
        context = ssl._create_unverified_context()
        url = myconf.get('api_tp.operaciones') + '/' + id +'/'
        req = Request(url, method='OPTIONS')
        with urlopen(req, context=context) as res:
            data = load(res)
        res = {}
        if ('actions' in data):
            res = dict(
                estados=data['actions']['PUT']['estados']['choices'],
                mantenimiento=data['actions']['PUT']['mantenimiento']['choices'],
                piezas_pendientes=data['actions']['PUT']['piezas_pendientes']['choices'],
                piezas_cierre=data['actions']['PUT']['piezas_cierre']['choices'],
                piezas_mtto=data['actions']['PUT']['piezas_mtto']['choices'],
            )
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
