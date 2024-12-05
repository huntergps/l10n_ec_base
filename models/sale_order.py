# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    uom_ids_allowed = fields.Many2many('uom.uom', compute='_compute_uom_ids_allowed', string='UdM Permitidos')

    @api.depends('product_template_id')
    def _compute_uom_ids_allowed(self):
        for line in self:
            if line.product_template_id:
                uom_records = line.product_template_id.sale_uom_ids
                if line.product_template_id.uom_id not in uom_records:
                    uom_records |= line.product_template_id.uom_id
                line.uom_ids_allowed = uom_records
            else:
                line.uom_ids_allowed = self.env['uom.uom']

    @api.onchange('product_template_id')
    def _compute_uom_ids_allowed_onchange(self):
        self._compute_uom_ids_allowed()
