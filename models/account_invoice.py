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

    edoc_import_id = fields.Many2one('l10n_ec_base.edoc.import',
        string='Documento de Importación',
        readonly=True
        )
    total_descuento_xml = fields.Monetary(string='Descuento XML')
    total_xml = fields.Monetary(string='Total XML')

    diferencia_xml = fields.Monetary(string='Diferencia XML',
        store=True, readonly=True, compute='_compute_diff_import')

    @api.depends('line_ids.debit', 'line_ids.credit','total_xml','amount_total')
    def _compute_diff_import(self):
        for order in self:
            total_xml = order.total_xml or 0.0
            total_sri = order.amount_total or 0.0
            order.diferencia_xml=total_sri-total_xml



class AccountMoveLine(models.Model):
    """ Override AccountInvoice_line to add the link to the purchase order line it is related to"""
    _inherit = 'account.move.line'
