# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_count = fields.Integer(string='Credit Note', compute='_compute_invoice_count')

    def _compute_invoice_count(self):
        """
        @desc: For count the credit note which are created from return delivery order.
        """
        for picking in self:
            move_ids = picking.env['account.move'].search([('invoice_origin', '=', picking.name)])
            self.invoice_count = move_ids and len(move_ids) or 0

    def action_open_picking_invoice(self):
        """
        @desc: For redirect to the credit note related to the current picking.
        @return: Action for latest created credit note.
        """
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('invoice_origin', '=', self.name)],
            'context': {'create': False},
            'target': 'current'
        }
