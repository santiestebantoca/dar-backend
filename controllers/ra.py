# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


"""
DAR Model:
provincia (not in SIPREC model): PK (id)  // What is that for?
region: PK (id[SIPREC])
territorio: PK (id[SIPREC]), FK (provincia_id, region_id)
area (not in SIPREC model): PK (id), FK (territorio_id)
central: PK (id[SIPREC], region_id), FK (area_id, region_id)
zona: PK (id), FK (area_id)
// there are some other important entities 
grupo: PK (id)
smsgrupo: PK (id)
destinatario: PK (id)
destinatario_area: PK (id), FK (destinatario_id, area_id)
destinatario_grupo: PK (id), FK (destinatario_id, grupo_id)
destinatario_smsgrupo: PK (id), FK (destinatario_id, smsgrupo_id)
//
asignacion: PK (id), FK (destinatario_id, zona_id, [central_id, region_id])
despachado: PK (id), Index (telefono, folio, iddt, grupo)
"""

"""
Webservice::Pendientes (data fields):
folio: report identifier
grupo: corresponds to `grupo`.`nombre`
centro + telefono: reported service (E.g. 33 + 200531)
idplantas: correspond to `central`.`id`
idcentel: (we don't use it at all, so it is not in DAR model)
iddt: correspond to `territorio`.`id` /* iddt comes in a two digits format, e.g. 04 */
zona: corresponds to `zona`.`nombre`
region: correspond to `region`.`id`

Important: (folio, iddt, grupo) is the dispatch case identifier

Cuando creo una asignación, inserto en asignacion...
x central/
  destinatario_id = destinatario.id (I)
  central_id = central.id (S)
  region_id = central.region_id (S)
  
x zona/
  destinatario_id = destinatario.id (I)
  zona_id = zona.id (I)
  

| zona |- id (I)
       |- nombre (S)
       |- area_id (I) <-> | area |- id (I)
                                 |- territorio_id (S) <-> | territorio |- id (S)
                                                                       |- region_id (S)
                                                                       |- provincia_id (S) [no se usa]
| central |- id (S)
          |- region_id (S)
          |- area_id (S)
"""


@request.restful()
def zonas():
    def GET(*args, **vars):
        return response.json(db(db.zona.area_id == vars['area_id']).select())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def centrales():
    def GET(*args, **vars):
        return response.json(db(db.central.area_id == vars['area_id']).select())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def asignaciones():

    def GET(*args, **vars):
        area = vars['area_id']
        usuario = auth.user_id
        res = db.executesql('call asignaciones({}, {})'.format(area, usuario))
        return response.json(res)

    def POST(*args, **vars):
        destinatario = request.vars.destinatario_id
        zona = request.vars.zona_id or 'NULL'
        central = request.vars.central_id or 'NULL'
        region = request.vars.region_id or 'NULL'
        create_by = auth.user_id
        res = db.executesql('call asignar({}, {}, {}, {}, {})'.format(
            destinatario, zona, central, region, create_by))[0][0]
        return response.json({'errors': {}, 'id': res})

    def DELETE(id, **vars):
        db.executesql(
            'call terminar_asignacion({},{})'.format(id, auth.user_id))
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
            from applications.dar.modules.db.despachador import reportes_ra
            return response.json(reportes_ra(db, auth, Storage(vars)))

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def despachado():
    def GET(*args, **vars):
        """
        (folio, iddt, grupo)
        returns:: telefono, anombre, despachador, enfecha, buzon_desahabilitado
        """
        rows = db(
            (db.despachado.folio == vars['folio'])
            & (db.despachado.iddt == vars['iddt'])
            & (db.despachado.grupo == vars['grupo'])
        ).select(
            db.despachado.telefono,
            db.despachado.anombre,
            db.despachado.enfecha,
            db.despachado.despachador,
            db.despachado.buzon_deshabilitado,
            db.despachado.confirmacion_entrega
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
            (db.despachado.folio == vars['folio'])
            & (db.despachado.iddt == vars['iddt'])
            & (db.despachado.telefono == vars['telefono'])
        ).update(buzon_deshabilitado=True)
        return response.json(res)

    def POST(*args, **vars):
        """
        This function uses the API "http://10.30.12.8/api/despachar.php"
        (API url configuration in appconfig.ini)
        API:
        ::does:
        1. Gets the report data from dar.wspendientes_central (<=> SIPREC Webservice Pendientes)
        2. Generates message (text) and sends SMS to 'telefono'
        3. Updates dar.despachado
        ::params:
        folio, grupo, iddt,          // reporte
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
        url = myconf.get('api_ra_reportes.despachar')
        data_encode = urlencode(vars).encode()  # to binary
        with urlopen(url, data_encode) as res:  # using POST method
            binary = res.read()
            return response.json(binary.decode())  # to str
    

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def ordenes():
    def GET(*args, **vars):
        res = db(db.wsordeneserv_central.area_id == vars['area_id']).select()
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def despachado_os():

    def GET(*args, **vars):
        """
        (idorden, idregion)
        returns:: telefono, anombre, despachador, enfecha, buzon_desahabilitado
        """
        rows = db(
            (db.despachado_os.idorden == vars['idorden'])
            & (db.despachado_os.idregion == vars['idregion'])
        ).select(
            db.despachado_os.telefono,
            db.despachado_os.anombre,
            db.despachado_os.enfecha,
            db.despachado_os.despachador,
            db.despachado_os.buzon_deshabilitado,
            db.despachado_os.confirmacion_entrega
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
            (db.despachado_os.idorden == vars['idorden'])
            & (db.despachado_os.idregion == vars['idregion'])
            & (db.despachado_os.telefono == vars['telefono'])
        ).update(buzon_deshabilitado=True)
        return response.json(res)

    def POST(*args, **vars):
        """
        This function uses the API "http://10.30.12.8/api/despachar_os.php"
        (API url configuration in appconfig.ini)
        API:
        ::does:
        1. Gets the report data from dar.wsordeneserv_central (<=> SIPREC Webservice OrdeneServ)
        2. Generates message (text) and sends SMS to 'telefono'
        3. Updates dar.despachado_os
        ::params:
        idorden, idregion,           // orden
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
        url = myconf.get('api_ra_ordenes.despachar')
        data_encode = urlencode(vars).encode()  # to binary
        with urlopen(url, data_encode) as res:  # using POST method
            binary = res.read()
            return response.json(binary.decode())  # to str

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
