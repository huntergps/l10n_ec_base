# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import html_translate

class ProductTemplate(models.Model):
    _inherit = "product.template",


    website_description = fields.Html(
        string="Description for the website",
        translate=html_translate,
        sanitize_overridable=True,
        sanitize_attributes=False, sanitize_form=False
    )
    website_description_ec = fields.Html('Descripcion del Sitio Web', sanitize_attributes=True)
    description_sale_ec = fields.Html(
        'Descripción de Ventas', translate=True, sanitize_attributes=True)
    sku = fields.Char('SKU', index=True)
    part_number = fields.Char('Nro de Parte', index=True)
    external_id = fields.Char('Id DB Externa',index=True)


    sale_uom_ids = fields.Many2many(
        'uom.uom',
        'product_template_uom_sale_rel',
        'template_id',
        'uom_id',
        string='Unidades de Medida permitidas en Ventas',
        tracking=True,
        help="Seleccione las Unidades de Medida permitidas en Ventas"
    )

    purchase_uom_ids = fields.Many2many(
        'uom.uom',
        'product_template_uom_purchase_rel',
        'template_id',
        'uom_id',
        string='Unidades de Medida permitidas en Compras',
        tracking=True,
        help="Seleccione las Unidades de Medida permitidas en Compras"
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    last_purchase_price = fields.Float(string="Ultimo Costo")
