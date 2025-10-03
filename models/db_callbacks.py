# coding: utf8


def check_usuario_area(x):
    """
    This procedure prevents a user without an area from being able to log in.
    In addition, it is remove from database to be created later by an administrator
    """
    usuario_tiene_area = db(db.usuario_area.usuario_id == auth.user_id).count() > 0
    if not usuario_tiene_area:
        db(db.auth_user.id == auth.user_id).delete()
        auth.logout()


auth.settings.login_onaccept = [check_usuario_area]

# [R-2408-2] Terminar asignaciones del destinatario cuando se le quita el smsgrupo "Pendiente"
def destinatario_smsgrupo_delete(s):
    if request.vars.smsgrupo_id == 1:
        db.executesql('call terminar_asignaciones_destinatario({}, {})'.format(
            request.vars.destinatario_id, auth.user_id
        ))

db.destinatario_smsgrupo._after_delete.append(destinatario_smsgrupo_delete)
