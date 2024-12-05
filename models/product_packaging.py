# # Copyright 2020 Camptocamp SA
# # License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
# from odoo import api, fields, models, tools, _
# from odoo.tools import float_repr
#
#
# class ProductPackaging(models.Model):
#     _inherit = "product.packaging"
#
#     compute_price = fields.Selection([
#         ('fixed', 'Precio Fijo'),
#         ('percentage', 'Porcentaje Descuento')], index=True, default='percentage', required=True, string='Tipo de  Calculo')
#     fixed_price = fields.Float('Fixed Price', digits='Precio Fijo')
#     percent_price = fields.Float('Porcentaje Descuento',default=0.0)
#     price = fields.Char(
#         'Precio', compute='_get_pricelist_item_name_price')
#
#     @api.depends('compute_price', 'fixed_price', 'percent_price')
#     def _get_pricelist_item_name_price(self):
#         currency_id = self.env.user.company_id.currency_id
#         for item in self:
#             if item.compute_price == 'fixed':
#                 decimal_places = self.env['decimal.precision'].precision_get('Product Price')
#                 if currency_id.position == 'after':
#                     item.price = "%s %s" % (
#                         float_repr(
#                             item.fixed_price,
#                             decimal_places,
#                         ),
#                         currency_id.symbol,
#                     )
#                 else:
#                     item.price = "%s %s" % (
#                         currency_id.symbol,
#                         float_repr(
#                             item.fixed_price,
#                             decimal_places,
#                         ),
#                     )
#             elif item.compute_price == 'percentage':
#                 item.price = _("%s %% de descuento") % (item.percent_price)
#
#
#     @api.onchange('compute_price')
#     def _onchange_compute_price(self):
#         if self.compute_price != 'fixed':
#             self.fixed_price = 0.0
#         if self.compute_price != 'percentage':
#             self.percent_price = 0.0
