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

    edoc_import_id = fields.Many2one('l10n_ec_base.edoc.import',
        string='Documento de Importación',
        readonly=True
        )
    total_descuento_xml = fields.Monetary(string='Descuento XML')
    total_xml = fields.Monetary(string='Total XML')

    diferencia_xml = fields.Monetary(string='Diferencia XML',
        store=True, readonly=True, compute='_compute_diff_import')

    # secuencial_completo_factura = fields.Char('Nro de Factura', compute='get_sri_secuencial_completo_factura', store=True)

    type_invoice_compra = fields.Selection([
        ('in_invoice', 'Documento con Validez Tributaria'),
        ('gasto', 'Documento sin Validez Tributaria')
    ], string='Documento Tributario', default='in_invoice')


    def _prepare_invoice(self):
        res= super(PurchaseOrder, self)._prepare_invoice()
        # res['type']=self.type_invoice_compra or 'in_invoice'
        # move_type = self._context.get('default_move_type', 'in_invoice')
        
        return res


    # @api.depends('establecimiento','puntoemision','secuencial')
    # def get_sri_secuencial_completo_factura(self):
    #     for rec in self:
    #         nro= '-'.join([
    #             rec.establecimiento or '0',
    #             rec.puntoemision or '0',
    #             (rec.secuencial or '0').zfill(9)
    #         ])
    #         rec.secuencial_completo_factura=nro or rec.partner_ref

    @api.depends('order_line.price_total','total_xml','amount_total')
    def _compute_diff_import(self):
        for order in self:
            total_xml = order.total_xml or 0.0
            total_sri = order.amount_total or 0.0
            order.diferencia_xml=total_sri-total_xml
