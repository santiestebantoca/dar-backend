# -*- coding: utf-8 -*-

from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth, Service, PluginManager
from gluon.contrib.login_methods.ldap_auth import ldap_auth

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
request.requires_https()

myconf = AppConfig()  # en producción, quitar reload=True para ganar velocidad

db = DAL(myconf.get('db.dar_uri'), pool_size=myconf.get('db.pool_size'), check_reserved=['all'],
         # default value for table migration
         migrate=myconf.get('db.migrate'),
         migrate_enabled=False  # disable migration for all tables
         )

session.connect(request, response, db, masterapp=None)

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
# choose a style for forms
# response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
# response.form_label_separator = myconf.get('forms.separator')

# (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
# (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
# Here is sample code if you need for
# - email capabilities
## - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
#########################################################################


auth = Auth(db)
service = Service()
plugins = PluginManager()

# extra fields
auth.settings.extra_fields['auth_user'] = [auth.signature]

# create all tables needed by auth if not custom tables
auth.define_tables(username=True)

# configure email
mail = auth.settings.mailer
# mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
# mail.settings.sender = myconf.get('smtp.sender')
# mail.settings.login = myconf.get('smtp.login')

# configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True
auth.settings.remember_me_form = False
auth.settings.create_user_groups = False
auth.settings.actions_disabled = ['register', 'change_password', 'request_reset_password', 'retrieve_username',
                                  'profile', ]
auth.settings.expiration = 60 * 60 * 10  # 10 hrs

# ds.etecsa.cu
# auth.settings.login_methods.append(
#     ldap_auth(
#         server='192.168.91.114',
#         base_dn='ou=etecsa.cu,ou=People,dc=etecsa,dc=cu')
# )

# lds.etecsa.cu
auth.settings.login_methods.append(
    ldap_auth(
        server='172.29.30.200',
        base_dn='ou=etecsa.cu,ou=People,dc=etecsa,dc=cu',
        secure=True,
        self_signed_certificate=True,
        # tls=True,
        logging_level='debug')
)

#########################################################################
# Define your tables below (or better in another model file) for example
##
# >>> db.define_table('mytable',Field('myfield','string'))
##
# Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
##
# More API examples for controllers:
##
# >>> db.mytable.insert(myfield='value')
# >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
#########################################################################

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

tabla = db.define_table

T.force('es')

"""
As long as possible, we use validate_and_update/insert rather than update or SQLFORM
* validate_and_update returns an Object with 'updated' and 'errors' which is a standard on client side
* validate_and_insert returns an Object with 'id' and 'errors' which is a standard on client side
"""

# CORS Policy (RESTFUL API )
"""
Using X-Requested-With header, implies using OPTIONS for any method (GET, POST, ...)
We force X-Requested-With: XMLHttpRequest in client request,
that is the way web2py recognizes the ajax request.
"""

if request.ajax:
    def resp403(): raise HTTP(403, 'Not authorized')
    auth.settings.on_failed_authorization = resp403

# frontURL = myconf.get('front.url', request.env.http_origin)
frontURL = request.env.http_origin

response.headers['Access-Control-Allow-Origin'] = frontURL
response.headers['Access-Control-Allow-Credentials'] = 'true'

headers = {
    'Access-Control-Allow-Origin': frontURL,
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Headers': 'X-Requested-With, Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT',
    # 24hrs  // cache for Allow Header & Allow Methods
    'Access-Control-Max-Age': 86400,
}
