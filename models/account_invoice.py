# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import difflib
import logging
import time
from markupsafe import Markup

from odoo import api, fields, models, Command, _

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
