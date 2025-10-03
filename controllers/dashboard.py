# -*- coding: utf-8 -*-
__author__ = 'jorge.santiesteban'


@request.restful()
def database():
    def GET():
        t = request.args(0) or ['asignacion', 'pendiente', 'profile']
        d = {}
        if 'asignacion' in t:
            d.update(
                asignacion=dict(
                    registros=db(db.asignacion.id > 0).count(),
                    inactivos=db(db.asignacion.termina != None).count()
                ))
        if 'pendiente' in t:
            d.update(
                pendiente=dict(
                    registros=db(db.pendiente.id > 0).count(),
                    repetidos=db(db.repetidos_en_pendiente.folio > 0).count()
                ))
        if 'profile' in t:
            def min_fecha():
                min_ = db.profile.ejecutado.min()
                rows = db(db.profile.id > 0).select(min_)
                return rows.first()[min_] if rows else ''

            d.update(
                profile=dict(
                    registros=db(db.profile.id > 0).count(),
                    minfecha=min_fecha()
                ))
        return response.json(d)

    def DELETE(table, **vars):
        if table == 'asignacion':
            res = db(db.asignacion.termina != None).delete()
        if table == 'pendiente':
            creado = request.now.strftime('%Y-%m-%d')
            res = db(db.pendiente.creado != creado).delete()
        if table == 'profile':
            from datetime import timedelta
            cero = dict(hour=0, minute=0, second=0, microsecond=0)
            semana = (request.now - timedelta(days=7)).replace(**cero)
            res = db(db.profile.ejecutado < semana).delete()
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def scripts():
    def GET(*args, **vars):
        from datetime import timedelta
        cero = dict(hour=0, minute=0, second=0, microsecond=0)
        # pendientes.php
        res = {}
        query = db.profile.proceso == 'pendientes'
        if request.vars.periodo == '1':
            query &= db.profile.ejecutado >= request.now.replace(**cero)
        elif request.vars.periodo == '2':
            query &= db.profile.ejecutado >= (
                request.now - timedelta(days=1)).replace(**cero)
            query &= db.profile.ejecutado < request.now.replace(**cero)
        elif request.vars.periodo == '3':
            query &= db.profile.ejecutado >= (
                request.now - timedelta(days=7)).replace(**cero)
            # query &= db.profile.ejecutado < request.now.replace(**cero)
        p, m = db.profile.tiempo.avg(), db.profile.tiempo.max()
        row = db(query).select(p, m).first()
        res['promedio'], res['maximo'] = row[p], row[m]
        rows = db(query).select(db.profile.ALL, orderby=db.profile.ejecutado)
        res['len_rows'] = len(rows)
        res['data'] = dict(
            labels=[row.ejecutado.strftime('%d %H:%M') for row in rows],
            datasets=[dict(
                # label='entrada',
                # fill=0,
                borderColor='#6b885a',
                data=[int(row.tiempo) for row in rows]
            )]
        )
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()


@request.restful()
def sms():
    def GET(*args, **vars):
        from datetime import timedelta
        smsgw = DAL(myconf.get('db.smsgw_uri'))
        rows = smsgw.executesql('call outbox_profile(%s)' % vars['periodo'])
        labels, data, total = [], [], 0
        for row in rows:
            labels.append(row[0][8:])
            data.append(row[1])
            total += row[1]
        datasets = [dict(borderColor='#6b885a', data=data)]
        res = dict(
            data=dict(labels=labels, datasets=datasets),
            total=total)
        return response.json(res)

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
