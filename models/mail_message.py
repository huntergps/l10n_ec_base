# my_module/models/res_partner.py
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

bypass_token = object()

class Message(models.Model):
    _inherit = 'mail.message'


    @api.ondelete(at_uninstall=True)
    def _except_audit_log(self):
        if self.env.context.get('bypass_audit') is bypass_token:
            return
        # Elimina la validación que impide eliminar registros del audit trail
        for message in self:
            if message.account_audit_log_activated:
                # Aquí removemos la restricción y permitimos que se elimine el registro
                # Quitamos la excepción para que se permita la eliminación completa
                pass
