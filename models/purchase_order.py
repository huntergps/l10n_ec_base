# -*- coding: UTF-8 -*-

from odoo import models, fields, api



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    uom_ids_allowed = fields.Many2many('uom.uom', compute='_compute_uom_ids_allowed', string='UdM Permitidos')

    @api.depends('product_id')
    def _compute_uom_ids_allowed(self):
        for line in self:
            if line.product_id:
                uom_records = line.product_id.purchase_uom_ids
                if line.product_id.uom_po_id not in uom_records:
                    uom_records |= line.product_id.uom_po_id
                line.uom_ids_allowed = uom_records
            else:
                line.uom_ids_allowed = self.env['uom.uom']
