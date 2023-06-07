# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    is_sample = fields.Boolean('Sample')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_approve(self):
        result = super(PurchaseOrder, self).button_approve()
        StockPicking = self.env['stock.picking']
        is_sample_pickings = self.order_line.filtered(lambda line: line.is_sample)
        move_ids = self.picking_ids.move_lines.filtered(lambda move: move.purchase_line_id.filtered(lambda line: line.is_sample))
        self.picking_ids.move_lines.write({'state':'draft'})
        self.picking_ids.move_lines = [(2, move_id.id) for move_id in move_ids]
        #For sample product 
        if is_sample_pickings:
            location = self.env['stock.location'].search([('is_sample_location','=',True)])
            wh = []
            for loc in location:
                warehouse = loc.get_warehouse()
                if self.picking_type_id.warehouse_id == warehouse and warehouse.id not in wh:
                    wh.append(warehouse.id)
                    res = {
                        'picking_type_id': self.picking_type_id.id,
                        'partner_id': self.partner_id.id,
                        'user_id': False,
                        'date': self.date_order,
                        'origin': self.name,
                        'location_dest_id': loc.id,
                        'location_id': self.partner_id.property_stock_supplier.id,
                        'company_id': self.company_id.id,
                        }
                    picking = StockPicking.create(res)
                    for is_sample_picking in is_sample_pickings:                   
                        move = self.env['stock.move'].create({
                            'name': is_sample_picking.product_id.partner_ref,
                            'location_id': self.partner_id.property_stock_supplier.id,
                            'location_dest_id': loc.id,
                            'product_id': is_sample_picking.product_id.id,
                            'product_uom': is_sample_picking.product_uom.id,
                            'picking_type_id': picking.picking_type_id.id,
                            'product_uom_qty': is_sample_picking.product_uom_qty,
                            'purchase_line_id': is_sample_picking.id,
                        })
                        picking.move_lines = [(4, mv.id)for mv in move]
                    self.picking_ids = [(4, picking.id)]
        self.picking_ids.action_confirm()
        return result