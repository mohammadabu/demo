# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        sale_order_line = []
        if self._context.get('sale_order_id'):
            sale_rec = self.env['sale.order'].browse(
                self._context.get('sale_order_id'))
            sale_order_line = sale_rec.order_line.filtered(
                lambda r: r.so_line_done == False).mapped('product_id').ids
            return self.search([('id', 'in', sale_order_line)]).name_get()
        else:
            return super(ProductProduct, self).name_search(name, args, operator, limit)
