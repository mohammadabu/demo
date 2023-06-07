# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_sample = fields.Boolean('Sample')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        """ This method set sample location when it is sample. """
        res = super(SaleOrder, self)._action_confirm()
        StockPicking = self.env['stock.picking']
        is_sample_pickings = self.order_line.filtered(lambda line: line.is_sample)
        move_ids = self.picking_ids.move_lines.filtered(lambda move: move.sale_line_id.filtered(lambda line: line.is_sample))
        self.picking_ids.move_lines.write({'state':'draft'})
        self.picking_ids.move_lines = [(2, move_id.id) for move_id in move_ids]
        #For sample product
        if is_sample_pickings:
            location = self.env['stock.location'].search([('is_sample_location','=',True)])
            wh = []
            for loc in location:
                warehouse = loc.get_warehouse()
                picking_type = self.env['stock.picking.type'].search([('code', '=','outgoing')])
                if self.warehouse_id == warehouse and warehouse.id not in wh:
                    wh.append(warehouse.id)
                    picking_values = {
                        'picking_type_id': picking_type[0].id,
                        'partner_id': self.partner_id.id,
                        'user_id': False,
                        'date': self.date_order,
                        'origin': self.name,
                        'location_dest_id': self.partner_id.property_stock_customer.id,
                        'location_id': loc.id,
                        'company_id': self.company_id.id,
                        }
                    picking = StockPicking.create(picking_values)
                    for is_sample_picking in is_sample_pickings:
                        move = self.env['stock.move'].create({
                            'name': is_sample_picking.product_id.partner_ref,
                            'location_id': loc.id,
                            'location_dest_id': self.partner_id.property_stock_customer.id,
                            'picking_type_id': picking.picking_type_id.id,
                            'product_id': is_sample_picking.product_id.id,
                            'product_uom': is_sample_picking.product_uom.id,
                            'product_uom_qty': is_sample_picking.product_uom_qty,
                        })
                        picking.move_lines = [(4, mv.id) for mv in move]
                        self.picking_ids = [(4, picking.id)]
        self.picking_ids.action_confirm()
        self.picking_ids.action_assign()
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        """ Create invoice with configure sample including invoice or not """
        res = super(SaleOrder, self)._create_invoices()
        for move in res:
            invoice_with_sample = self.env['ir.config_parameter'].sudo().get_param('sync_sample_product.invoice_with_sample')
            is_sample_lines = move.invoice_line_ids.filtered(lambda move: move.sale_line_ids.filtered(lambda line: line.is_sample))
            if is_sample_lines and not invoice_with_sample:
                move.invoice_line_ids = [(2, is_sample_line.id) for is_sample_line in is_sample_lines]
        return res