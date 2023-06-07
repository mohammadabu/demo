from socket import timeout

from gevent import Timeout
from odoo import SUPERUSER_ID, api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class Edit_Sales(models.Model):
    _inherit = "sale.order.line"
    _description = "Sales Order Line"
    is_qty_delivered_less = fields.Boolean(compute='_compute_is_qty_delivered_less', store=True)
    qty_delivered_is_less = fields.Char(string=" ", store=True)

    @api.depends('product_id', 'state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_is_qty_delivered_less(self):
        """ This method compute the delivered quantity if less than ordered quantity.
        """
        for sale_line in self:
            _logger.debug('sale_line_order_id_state %s', sale_line.order_id.state)
            if (sale_line.qty_delivered < sale_line.product_uom_qty and sale_line.order_id.state in ['sale', 'done']):
                sale_line.is_qty_delivered_less = False
                sale_line.qty_delivered_is_less = "Quantity Delivered Is Less than Quantity Ordered"
            else:
                sale_line.qty_delivered_is_less = " "
                sale_line.is_qty_delivered_less = True

    @api.onchange('product_id', 'product_uom_qty')
    def product_id_change(self):
        domian = super(Edit_Sales, self).product_id_change()
        ids_to_exc = []
        for order in self.order_id:
            for product in order.order_line:
                res = {}     
                available_quantity = 0
                stock_qty = self.env['stock.quant'].sudo().search([('product_id','=',product.product_id.id), ('on_hand', '=', True)])
                for qty in stock_qty:
                    available_quantity += qty.available_quantity
                if (available_quantity > 0):
                    if (product.product_uom_qty > available_quantity):
                        if (product.product_id.id not in ids_to_exc):
                            ids_to_exc.append(product.product_id.id)
                            res = {
                                'warning': {
                                    'title': _('Warning'),
                                    'message': _('Not enough stock ! You requested '+ str(product.product_uom_qty) +'. The available stock i '+ str(available_quantity) +' !')
                                }
                            }
                if res:
                    return res
        return domian