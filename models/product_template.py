# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import html_translate

class ProductTemplate(models.Model):
    _inherit = "product.template",


    website_description = fields.Html(
        string="Description for the website",
        translate=html_translate,
        sanitize_overridable=True,
        sanitize_attributes=False,
        sanitize_form=False,
    )
    website_description_ec = fields.Html('Descripcion del Sitio Web', sanitize_attributes=True)
    description_sale_ec = fields.Html(
        'Descripción de Ventas', translate=True, sanitize_attributes=True)

    sku = fields.Char('SKU', index=True)
    part_number = fields.Char('Nro de Parte', index=True)
    external_id = fields.Char('Id DB Externa',index=True)

    # @api.model
    # def create(self, vals):
    #     print("CREAR TEMPLATE>> \n",vals)
    #     return super(ProductTemplate, self).create(vals)
    #
    # def write(self, vals):
    #     # print(vals)
    #     if 'standard_price'  in vals:
    #         if 'id' in vals:
    #             print("ACTUALIZAR TEMPLATE>> \n",vals['id'],"  -> ", vals['standard_price'])
    #         else:
    #             print("ACTUALIZAR TEMPLATE>> \n", vals['standard_price'])
    #
    #     return super(ProductTemplate, self).write(vals)



class ProductProduct(models.Model):
    _inherit = "product.product"

    last_purchase_price = fields.Float(string="Ultimo Costo")
