# my_module/models/res_partner.py
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError



class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"
