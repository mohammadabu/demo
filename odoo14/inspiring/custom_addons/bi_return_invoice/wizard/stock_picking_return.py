# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    has_invoices = fields.Boolean('Has Invoices?', compute='_compute_has_invoices', store=True)
    picking_type = fields.Selection(related='picking_id.picking_type_id.code')

    @api.depends('picking_id', 'picking_id.sale_id', 'picking_id.sale_id.invoice_ids')
    def _compute_has_invoices(self):
        """
        @desc: To check the order has invoices or not.
        """
        for picking in self:
            picking.has_invoices = picking.picking_id and picking.picking_id.sale_id and picking.picking_id.sale_id.invoice_ids and True or False
