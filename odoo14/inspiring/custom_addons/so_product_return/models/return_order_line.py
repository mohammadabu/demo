# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ReturnOrderLine(models.Model):
    _name = "return.order.line"
    _description = "Return Order Line"

    return_order_id = fields.Many2one(
        'return.order', string='Return Order', copy=False)
    product_id = fields.Many2one(
        'product.product', string='Product', copy=False)
    return_reason_id = fields.Many2one(
        'return.reason', string='Return Reason', copy=False)
    deliver_qty = fields.Float(string='Delivered Quantity', copy=False)
    quantity = fields.Float(string='Return Quantity', copy=False)
    remain_qty = fields.Float(string='Remaining Quantity', copy=False)
    main_qty = fields.Float(string='Main Quantity', copy=False)
    unit_price = fields.Float(string='Unit Price', copy=False)
    sale_order_line_id = fields.Many2one(
        'sale.order.line', string='Sale Order Line', copy=False)
    qty_to_select = fields.Float(
        string='Qty selected', related='sale_order_line_id.qty_to_select')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    sale_order_id = fields.Many2one(
        'sale.order', string='Sale Order', copy=False, related='return_order_id.order_id')
    subtotal = fields.Float(
        'Sub Total', compute='compute_total', store=True, copy=False)
    # tax_id = fields.Many2many(related="sale_order_line_id.tax_id", copy=False)
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    product_found = fields.Boolean(string='Product Found', copy=False)

    @api.model
    def create(self, vals):
        if vals.get('quantity') == 0.0:
            raise ValidationError(_(
                "Please enter return quantity greater than 0"))
        return super(ReturnOrderLine, self).create(vals)

    @api.depends('quantity', 'unit_price')
    def compute_total(self):
        for rec in self:
            amount = 0
            amount += rec.quantity * rec.unit_price
            rec.subtotal = amount

    @api.onchange('product_id')
    def onchange_product(self):
       
        # if self.return_order_id and not self.return_order_id.order_id:
        #     raise UserError(
        #         _("Please select customer and sale order first"))
        # if self.return_order_id and not self.return_order_id.order_id.picking_ids:
        #     raise UserError(
        #         _("Please validate the picking of selected sale order and then try to return the product"))
        # else:
        if self.product_id:
            picking_ids = self.env['stock.picking'].search(
                [('sale_id', '=', self.sale_order_id.id)])
            out_qty = 0
            in_qty = 0
            total_in_qty = 0
            if picking_ids:
                for picking in picking_ids:
                    if picking.picking_type_code == 'outgoing' and picking.state == 'done':
                        for line in picking_ids.move_ids_without_package:
                            if self.product_id == line.product_id and line.state == 'done' and line.picking_id == picking:
                                out_qty += line.quantity_done
                    if picking.picking_type_code == 'incoming':
                        for line in picking_ids.move_ids_without_package:
                            if self.product_id == line.product_id and line.picking_id == picking:
                                if picking.state == 'done':
                                    in_qty = line.quantity_done
                                    if total_in_qty == 0:
                                        total_in_qty = in_qty
                                    else:
                                        total_in_qty = total_in_qty + in_qty
                line_id = self.env['sale.order.line'].search(
                    [('order_id', '=', self.sale_order_id.id), ('product_id', '=', self.product_id.id)], limit=1)
                if line_id:
                    self.sale_order_line_id = line_id
                    self.unit_price = line_id.price_unit
                self.deliver_qty = out_qty
                if line_id and not line_id.product_called or self.qty_to_select == 0:
                    self.main_qty = out_qty - total_in_qty
                    self.remain_qty = out_qty - total_in_qty
                else:
                    self.main_qty = self.qty_to_select
                    self.remain_qty = self.qty_to_select

    @api.onchange('quantity')
    def onchange_quantity(self):
        line_id = self.env['sale.order.line'].search(
            [('order_id', '=', self.sale_order_id.id), ('product_id', '=', self.product_id.id)])
        if self.quantity and line_id:
            line_id.write({'qty_to_select': self.remain_qty - self.quantity, 'product_called': True})
        else:
            line_id.write({'qty_to_select': 0, 'product_called': False})
        # if self.quantity and self.main_qty:
        #     if self.quantity == 0.0:
        #         raise ValidationError(_(
        #             "Please enter return quantity greater than 0"))
        #     if self.quantity > self.main_qty:
        #         raise ValidationError(_(
        #             "Sorry ! You cannot enter %s quantity as it exceeds original Remaining Quantity." % (self.quantity)))
