# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    return_count = fields.Integer(
        compute='_compute_return_count', string='Return Count', copy=False)
    so_done = fields.Boolean(string='SO Done', copy=False)

    def name_get(self):
        result = []
        for rec in self:
            name = '%s - %s' % (rec.name, rec.partner_id.name)
            result.append((rec.id, name))
        return result

    def _compute_return_count(self):
        """ It counts total number of return """
        self.return_count = self.env['return.order'].search_count(
            [('order_id', '=', self.id)])


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_to_select = fields.Float(string='Qty selected', copy=False)
    deliver_qty = fields.Float(string='Deliver Quantity', copy=False)
    total_in_qty = fields.Float(
        string='Total In Quantity', copy=False)
    so_line_done = fields.Boolean(
        string='SO Line Done', compute='_compute_line_done', copy=False)
    product_called = fields.Boolean(string='Product added', copy=False)

    @api.depends('qty_delivered')
    def _compute_line_done(self):
        order_id = ""
        for record in self:
            order_id = record.order_id
            picking_id = self.order_id.picking_ids.filtered(
                lambda r: r.picking_type_code == 'outgoing' and r.state == 'done')
            if picking_id:
                if record.qty_delivered <= 0.0:
                    record.so_line_done = True
                else:
                    record.so_line_done = record.so_line_done
                line_ids = order_id.order_line.filtered(
                    lambda r: r.so_line_done == False)
                if not line_ids:
                    order_id.so_done = True
                else:
                    order_id.so_done = False
            else:
                record.so_line_done = record.so_line_done

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom', 'deliver_qty', 'total_in_qty')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()
        for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
            if line.qty_delivered_method == 'stock_move':
                qty = 0.0
                outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
                for move in outgoing_moves:
                    if move.state != 'done':
                        continue
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                for move in incoming_moves:
                    if move.state != 'done':
                        continue
                    qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                line.qty_delivered = qty


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for picking in self:
            if picking.picking_type_code == 'incoming':
                order_ids = self.env['sale.order.line'].search(
                    [('order_id', '=', self.sale_id.id)])
                if order_ids:
                    for picking_line in self.move_ids_without_package:
                        for order_line in order_ids:
                            if order_line.product_id == picking_line.product_id:
                                if order_line.qty_delivered == 0.0:
                                    raise UserError(
                                        _("Cannot validate the return order as product is unavailable."))
        return super(StockPicking, self).button_validate()

    ret_in_state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operations'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='Ret Status',
        copy=False, index=True, compute="compute_ret_status", store=True)

    @api.depends('state')
    def compute_ret_status(self):
        for picking in self:
            if picking.picking_type_code == 'incoming':
                return_id = self.env['return.order'].search(
                    [('in_picking_id', '=', picking.id)])
                return_id.write({'return_in_state': picking.state})
                return_id.return_in_state = picking.state
