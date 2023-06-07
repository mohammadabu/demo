# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round
import logging
from odoo.http import request
_logger = logging.getLogger(__name__)
class ReturnOrder(models.Model):
    _name = "return.order"
    _description = "Returns"
    _rec_name = "return_numb"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    return_numb = fields.Char(string='Return Number', readonly=True,
                              required=True, copy=False, default=lambda self: 'New')
    user_id = fields.Many2one(
        'res.users', string='Sales Person', default=lambda self: self.env.user, copy=False)
    date = fields.Datetime(string="Date", required=False, readonly=False,
                           default=lambda self: fields.datetime.now(), copy=False)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True)
    order_id = fields.Many2one('sale.order', string='Sale Order', copy=False)
    return_order_line_ids = fields.One2many(
        'return.order.line', 'return_order_id', string='Return Record Lines', copy=False)
    total_amount = fields.Float(
        'Amount Untaxed', compute='compute_total', store=True, readonly=True)
    in_picking_id = fields.Many2one(
        'stock.picking', string='Picking IN', copy=False)
    delivery_count = fields.Integer(
        compute='_compute_delivery_count', string='Delivery Count', copy=False)
    return_pickings_count = fields.Integer(
        compute='_compute_return_count', string='Return Picking Count', copy=False)
    state = fields.Selection([('draft', 'Draft'), ('approved', 'In Progress'), ('cancel', 'Cancelled'),
                              ('returned', 'Ready to Return')], required=True, default='draft', copy=False, tracking=True)
    return_in_state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operations'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='Return Status',
        copy=False, index=True, compute="compute_return_status", store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    amount_tax = fields.Monetary(
        string='Taxes', store=True, readonly=True, compute='_compute_tax_amount')
    final_total = fields.Monetary(
        string="Total", store=True, readonly=True, compute='_compute_final_total')
        
    # added by zakaria alyafawi to handle the RTV documents, date and nunmber.
    RTV_Doc = fields.Binary(string='RTV Document', attachment=True, required=True)
    RTV_Date = fields.Date(string='RTV Date', default=date.today(), required=True)
    RTV_num = fields.Integer(string='RTV Number', required =True)

    check_position = fields.Boolean(compute='check_user_group_position')

    # to check the user group position, this procedure will be used to hid create, create and ecit for spicific group position.
    def check_user_group_position(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        if user.has_group('sales_team.group_sale_manager'):
            _logger.info('==========================>> True')
            self.check_position = True
        else:
            _logger.info('==========================>> false')
            self.check_position = False


    @api.depends('amount_tax', 'total_amount')
    def _compute_final_total(self):
        """Compute final total"""
        for order in self:
            order.final_total = order.amount_tax + order.total_amount

    @api.depends('return_order_line_ids.quantity', 'return_order_line_ids.unit_price', 'return_order_line_ids.tax_id')
    def _compute_tax_amount(self):
        """Compute the tax amount"""
        for order in self:
            amount_tax = 0.0
            for line in order.return_order_line_ids:
                for tax in line.tax_id:
                    amount_tax += line.quantity * line.unit_price * tax.amount / 100
            order.amount_tax = amount_tax

    @api.depends('in_picking_id')
    def compute_return_status(self):
        for record in self:
            if record.in_picking_id:
                record.return_in_state = record.in_picking_id.state

    @api.model
    def create(self, vals):
        if vals.get('return_numb', 'New') == 'New':
            vals['return_numb'] = self.env['ir.sequence'].next_by_code(
                'return.order') or 'New'
            return super(ReturnOrder, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            self.order_id = False
            self.return_order_line_ids = False
        else:
            self.order_id = False
            self.return_order_line_ids = False

    @api.depends('return_order_line_ids.subtotal')
    def compute_total(self):
        for rec in self:
            amount = 0
            for order in rec.return_order_line_ids:
                amount += order.subtotal
            rec.update({
                'total_amount': amount
            })

    def _compute_delivery_count(self):
        """ It counts total number of delivery """
        for record in self:
            record.delivery_count = 0
            if record.order_id:
                record.delivery_count = self.env['stock.picking'].search_count(
                    [('sale_id', '=', record.order_id.id), ('picking_type_code', '=', 'outgoing')])

    def action_picking_delivery(self):
        tree_view_id = self.env.ref('stock.vpicktree').id
        return {
            'name': 'Delivery Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (False, 'form')],
            'target': 'current',
            'domain': [('sale_id', '=', self.order_id.id), ('picking_type_code', '=', 'outgoing')],
            'context': {'create': False}
        }

    def _compute_return_count(self):
        """ It counts total number of return """
        for record in self:
            record.return_pickings_count = 0
            if record.order_id:
                record.return_pickings_count = self.env['stock.picking'].search_count(
                    [('sale_id', '=', record.order_id.id), ('picking_type_code', '=', 'incoming')])

    def action_return_pickings(self):
        tree_view_id = self.env.ref('stock.vpicktree').id
        return {
            'name': 'Return Pickings',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (False, 'form')],
            'target': 'current',
            'domain': [('sale_id', '=', self.order_id.id), ('picking_type_code', '=', 'incoming')],
            'context': {'create': False}
        }

    def unlink(self):
        for so_return in self:
            if so_return.state == 'returned':
                raise UserError(
                    _('You cannot delete this record as return request has already been made.'))
        return super(ReturnOrder, self).unlink()

    def get_out_picking(self):
        print('test')
    #     picking_id = ""
    #     picking_id = self.order_id.picking_ids.filtered(
    #         lambda r: r.picking_type_code == 'outgoing' and r.state == 'done')
        
    #     _logger = logging.getLogger(__name__)
    #     _logger.info('=======================================================>')
    #     _logger.info(picking_id)
    #     _logger.info(not picking_id)
    #     if not picking_id:
    #         raise UserError(
    #             _("Please validate the picking and then return the product."))
    #     else:
    #         return picking_id

    @api.onchange('order_id')
    def onchange_order(self):
        if self.order_id and self.order_id.picking_ids:
            picking_id = ""
            picking_id = self.order_id.picking_ids.filtered(
                lambda r: r.picking_type_code == 'outgoing' and r.state == 'done')
            if not picking_id:
                raise UserError(
                    _("Please validate the picking of selected sale order"))

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        quantity = stock_move.product_qty
        for move in stock_move.move_dest_ids:
            if move.origin_returned_move_id and move.origin_returned_move_id != stock_move:
                continue
            if move.state in ('partially_available', 'assigned'):
                quantity -= sum(move.move_line_ids.mapped('product_qty'))
            elif move.state in ('done'):
                quantity -= move.product_qty
        quantity = float_round(
            quantity, precision_rounding=stock_move.product_uom.rounding)
        return {
            'product_id': stock_move.product_id.id,
            'quantity': quantity,
            'move_id': stock_move.id,
            'uom_id': stock_move.product_id.uom_id.id,
        }

    def action_return(self):
        self.write({'state': 'returned'})
    #     if self.state == 'approved':

    #         for return_lines in self.return_order_line_ids:
    #             for order_line in self.order_id.order_line:
    #                 if order_line.product_id == return_lines.product_id:
    #                     order_line.write({'product_called': False})
    #                     if order_line.qty_delivered == 0.0:
    #                         raise UserError(
    #                             _("The selected product is unavailable."))

    #         picking_ids = self.get_out_picking()
    #         picking_id = picking_ids.filtered(lambda r: not r.backorder_id)
    #         if picking_id:
    #             move_dest_exists = False
    #             product_return_moves = [(5,)]
    #             if picking_id and picking_id.state != 'done':
    #                 raise UserError(_("You may only return Done pickings."))
    #             # In case we want to set specific default values (e.g. 'to_refund'), we must fetch the
    #             # default values for creation.
    #             line_fields = [
    #                 f for f in self.env['return.order.line']._fields.keys()]
    #             product_return_moves_data_tmpl = self.env['return.order.line'].default_get(
    #                 line_fields)
    #             for move in picking_id.move_lines:
    #                 if move.state == 'cancel':
    #                     continue
    #                 if move.scrapped:
    #                     continue
    #                 if move.move_dest_ids:
    #                     move_dest_exists = True
    #                 product_return_moves_data = dict(
    #                     product_return_moves_data_tmpl)
    #                 product_return_moves_data.update(
    #                     self._prepare_stock_return_picking_line_vals_from_move(move))
    #                 product_return_moves.append(
    #                     (0, 0, product_return_moves_data))
    #             if picking_id and not product_return_moves:
    #                 raise UserError(
    #                     _("No products to return (only lines in Done state and not fully returned yet can be returned)."))
    #             if picking_id:
    #                 location_id = picking_id.location_id.id
    #                 if picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
    #                     location_id = picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.id

    #             for return_move in picking_id.move_ids_without_package:
    #                 return_move.move_dest_ids.filtered(
    #                     lambda m: m.state not in ('done', 'cancel'))._do_unreserve()
    #             picking_type_id = picking_id.picking_type_id.return_picking_type_id.id or picking_id.picking_type_id.id
    #             new_picking = picking_id.copy({
    #                 'move_lines': [],
    #                 'picking_type_id': picking_type_id,
    #                 'state': 'draft',
    #                 'origin': _("Return of %s") % picking_id.name,
    #                 'location_id': picking_id.location_dest_id.id,
    #                 'location_dest_id': picking_id.location_id.id})
    #             new_picking.message_post_with_view('mail.message_origin_link',
    #                                                values={
    #                                                    'self': new_picking, 'origin': picking_id},
    #                                                subtype_id=self.env.ref('mail.mt_note').id)
    #             returned_lines = 0
    #             product_uom_qty = 0
    #             origin_name_list = []
    #             origin_name = ''
    #             for picking in picking_ids:
    #                 for return_line in picking.move_ids_without_package.filtered(lambda r: r.state == 'done'):
    #                     for line in self.return_order_line_ids:
    #                         if return_line.product_id.id == line.product_id.id and not line.product_found:
    #                             product_uom_qty = line.quantity
    #                             if new_picking and picking.name:
    #                                 if picking.name not in origin_name_list:
    #                                     origin_name_list.append(picking.name)
    #                                     if origin_name == '':
    #                                         origin_name = picking.name
    #                                     else:
    #                                         origin_name = origin_name + ',' + picking.name
    #                             line.write({'product_found': True})

    #                         # else:
    #                         #     product_uom_qty = return_line.product_uom_qty
    #                             if not return_line:
    #                                 raise UserError(
    #                                     _("You have manually created product lines, please delete them to proceed."))
    #                             if return_line.product_uom_qty:
    #                                 returned_lines += 1
    #                                 vals = {
    #                                     'product_id': return_line.product_id.id,
    #                                     'product_uom_qty': product_uom_qty,
    #                                     'product_uom': return_line.product_id.uom_id.id,
    #                                     'picking_id': new_picking.id,
    #                                     'state': 'draft',
    #                                     'date': fields.Datetime.now(),
    #                                     'location_id': return_line.location_dest_id.id,
    #                                     'location_dest_id': picking_id.location_id.id or return_line.location_id.id,
    #                                     'picking_type_id': new_picking.picking_type_id.id,
    #                                     'warehouse_id': picking_id.picking_type_id.warehouse_id.id,
    #                                     'origin_returned_move_id': return_line.id,
    #                                     'procure_method': 'make_to_stock',
    #                                     'to_refund': True
    #                                 }
    #                                 r = return_line.copy(vals)
    #                                 vals = {}
    #                                 move_orig_to_link = return_line.move_dest_ids.mapped(
    #                                     'returned_move_ids')
    #                                 move_dest_to_link = return_line.move_orig_ids.mapped(
    #                                     'returned_move_ids')
    #                                 vals['move_orig_ids'] = [
    #                                     (4, m.id) for m in move_orig_to_link | return_line]
    #                                 vals['move_dest_ids'] = [
    #                                     (4, m.id) for m in move_dest_to_link]
    #                                 r.write(vals)
    #             new_picking.write({'origin': _("Return of %s") % origin_name})
    #             if not returned_lines:
    #                 raise UserError(
    #                     _("Please specify at least one non-zero quantity."))
    #             self.in_picking_id = new_picking.id
    #             new_picking.action_confirm()
    #             new_picking.action_assign()
    #             return self.write({'state': 'returned'})

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_to_approve(self):
        if self.return_order_line_ids:
            if not self.order_id.so_done:
                # picking_id = self.get_out_picking()
                # if picking_id:
                return self.write({'state': 'approved'})
            else:
                return self.write({'state': 'cancel'})
        else:
            raise UserError(
                _("Cannot confirm the return order as product is not specified"))

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_done(self):
        return self.write({'state': 'done'})


class ReturnReason(models.Model):
    _name = "return.reason"
    _description = "Return Reason"
    _rec_name = "return_name"

    return_name = fields.Char(string='Reason Name')
