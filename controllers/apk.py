# -*- coding: utf-8 -*-
__author__ = "jorge.santiesteban"


@request.restful()
def index():

    def GET(*args, **vars):
        from os import path
        
        file = '/var/www/html/consultas/VERSION'
        content = ''
        
        if path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
        return response.json(dict(
            link='https://10.30.12.8/consultas/Consultas.apk',
            version=content,
            descargado=10
            ))

    def OPTIONS(*args, **vars):
        raise HTTP(200, **headers)

    return locals()
