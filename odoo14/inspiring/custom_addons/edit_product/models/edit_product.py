from odoo import api, fields, models, _
from lxml import etree
import json
import logging
_logger = logging.getLogger(__name__)

class Edit_Product(models.Model):
    _inherit = "product.template"
    _description = "Edit product fields"

    name_ar = fields.Char('Arabic Name')
    default_code = fields.Char('Internal Reference', readonly=True,
               index=True, default=lambda self: _('New'))
    barcode = fields.Char(
                'Barcode', copy=False, store=True, help="International Article Number used for product identification.")
    expiration_date = fields.Datetime(string='Expiration Date', readonly=True)

    @api.model
    def create(self, vals):
        vals['default_code'] = self.env['ir.sequence'].next_by_code('increment_your_field')
        res = super(Edit_Product, self).create(vals)
        return res

    # def write(self, vals):
    #     res = super(Edit_Product, self).write(vals)
    #     products = self.env['product.template'].sudo().search([], order="id asc")
        
    #     count = 0
    #     for product in products:
    #         if (not product.default_code):
    #             count = count+1
    #             product.default_code = self.env['ir.sequence'].next_by_code('increment_your_field')
    #     _logger.info('products_count %s', len(products))
    #     _logger.info('normal_count %s', count)
    #     vals['default_code'] = self.env['ir.sequence'].next_by_code('increment_your_field')
    #     return res