# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


"""
DAR Model:
territorio: PK (id[SIPREC]), FK (provincia_id, ...)
area (not in SIPREC nither SIGETP model): PK (id), FK (territorio, sigetp_ct_di)
zona_tp: PK (id[SIGETP]), FK (area)
// there are some other important entities 
grupo: PK (id)
smsgrupo: PK (id)
destinatario: PK (id)
destinatario_area: PK (id), FK (destinatario_id, area_id)
destinatario_grupo: PK (id), FK (destinatario_id, grupo_id)
destinatario_smsgrupo: PK (id), FK (destinatario_id, smsgrupo_id)
//
asignacion_tp: PK (id), FK (destinatario, zona_tp)
despachado_tp: PK (id), Index (telefono, averia_id)
"""

"""
pgsql://10.230.255.15:5432/sigetp/sch_dar.v_dar_averias_pendientes (relevant data fields):
id: report identifier, corresponds to `tpprocesado`.`id`, `despachado_tp`.`averia_id`
estados_pendientes: report status
id_ct: corresponds to `area`.`sigetp_ct_id`       (1)
id_zona: corresponds to `asignacion_tp`.`zona_id` (2)

Important: (averia_id, telefono) is the dispatch case identifier

(1) to asociate a report with an area
(2) this field is not store in `tppendiente`, it is only for php scripts use
"""


@request.restful()
def zonas():
    def GET(*args, **vars):
        return response.json(db(db.zona_tp.area_id == vars['area_id']).select())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def asignaciones():  # TODO: Check all this API. It is in the old pattern
    def GET(*args, **vars):
        area = vars['area_id']
        usuario = auth.user_id
        res = db.executesql(
            'call asignaciones_tp({}, {})'.format(area, usuario))
        return response.json(res)

    def POST(*args, **vars):
        destinatario = request.vars.destinatario_id
        zona = request.vars.zona_id
        create_by = auth.user_id
        res = db.executesql('call asignar_tp({}, {}, {})'.format(
            destinatario, zona, create_by))[0][0]
        return response.json({'errors': {}, 'id': res})

    def DELETE(id, **vars):
        db.executesql(
            'call terminar_asignacion_tp({},{})'.format(id, auth.user_id))
        return response.json({'updated': 1, 'errors': {}})

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def reportes():
    def GET(id=None, **vars):
        if id:
            pass
        else:
            from gluon.storage import Storage
            from applications.dar.modules.db.despachador import reportes_tp
            return response.json(reportes_tp(db, auth, Storage(vars)))
        
    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def despachado():
    def GET(*args, **vars):
        """
        (averia_id)
        returns:: telefono, anombre, despachador, enfecha, buzon_desahabilitado
        """
        rows = db(
            db.despachado_tp.averia_id == vars['averia_id']
        ).select(
            db.despachado_tp.telefono,
            db.despachado_tp.anombre,
            db.despachado_tp.enfecha,
            db.despachado_tp.despachador,
            db.despachado_tp.buzon_deshabilitado,
            db.despachado_tp.confirmacion_entrega
        )
        res = {}
        for row in rows:
            fecha = dict(
                enfecha=row.enfecha,
                despachador=row.despachador,
                buzon_deshabilitado=row.buzon_deshabilitado,
                recibo=row.confirmacion_entrega
            )
            if not row.telefono in res:
                res[row.telefono] = dict(
                    anombre=row.anombre,
                    days=row.days,
                    telefono=row.telefono,
                    fechas=[fecha]
                )
            else:
                res[row.telefono]['fechas'] += [fecha]
                if row.days < res[row.telefono]['days']:
                    res[row.telefono]['days'] = row.days
        return response.json(list(res.values()))

    def PUT(*args, **vars):
        res = db(
            (db.despachado_tp.averia_id == vars['averia_id']) &
            (db.despachado_tp.telefono == vars['telefono'])
        ).update(buzon_deshabilitado=True)
        return response.json(res)

    def POST(*args, **vars):
        """
        This function uses the API "http://10.30.12.8/api/despachar_tp.php"
        (API url_tp configuration in appconfig.ini)
        API:
        ::does:
        1. Gets the report data from SIGETP sch_dar.v_dar_averias_pendientes
        2. Generates message (text) and sends SMS to 'telefono'
        3. Updates dar.despachado_tp
        ::params:
        id,                          // reporte
        telefono, nombre             // destinatario
        despachador                  // despachador (= auth.user.username)
        ::returns:
        successful dispatch
        ? 1
        : 0
        """
        from urllib.request import urlopen
        from urllib.parse import urlencode
        vars['despachador'] = auth.user.username
        url = myconf.get('api_tp.despachar')
        data_encode = urlencode(vars).encode()  # to binary
        with urlopen(url, data_encode) as res:  # using POST method
            binary = res.read()
            return response.json(binary.decode())  # to str

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
