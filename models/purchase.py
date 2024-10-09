# -*- coding: utf-8 -*-
import unicodedata  # para normalizar el nombre
from collections import OrderedDict
from datetime import datetime

import pytz
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging

try:
    from suds.client import Client
except ImportError:
    logging.getLogger('xades.sri').info('Intente pip3 install suds-jurko')




class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
