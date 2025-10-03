# -*- coding: utf-8 -*-


@request.restful()
def index():

    def GET(*args, **vars):
        return response.json(db(db.info.id > 0).select(db.info.html).as_list())

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()