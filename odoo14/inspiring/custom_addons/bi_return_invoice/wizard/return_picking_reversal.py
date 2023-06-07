# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ReturnPickingReversal(models.TransientModel):
    _name = 'return.picking.reversal'
    _description = 'Return Picking Account Reversal'

    @api.model
    def default_get(self, fields):
        """
        @desc: To get the delivery order id from existing reversal wizard.
        @args: fields - dict: with all field values of current model.
        @return: fields - dict: with updated value of picking id field.
        """
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only return one picking at a time."))
        res = super(ReturnPickingReversal, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'stock.return.picking':
            picking = self.env['stock.return.picking'].browse(self.env.context.get('active_id'))
            if picking.exists():
                res.update({'picking_id': picking.picking_id and picking.picking_id.id})
        return res

    picking_id = fields.Many2one('stock.picking')
    reason = fields.Char(string='Reason')
    date = fields.Date(string='Reversal date', default=fields.Date.context_today, required=True)
    journal_id = fields.Many2one('account.journal', string='Use Specific Journal',
                                 help='If empty, uses the journal of the journal entry to be reversed.')

    def reverse_moves(self):
        """
        @desc: To create return delivery order & draft credit note from reversal wizard.
        @return: Action of new created return delivery order.
        """
        return_picking = None
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'stock.return.picking':
            return_picking = self.env['stock.return.picking'].browse(self.env.context.get('active_id'))

        # Create reverse stock moves (Return Delivery Order)
        for wizard in return_picking:
            new_picking_id, pick_type_id = wizard._create_returns()

        # Create reverse account moves (Credit Note)
        picking_id = new_picking_id and self.env['stock.picking'].browse(new_picking_id) or None
        moves = picking_id and picking_id.sale_id and self.env['account.move'].browse(
            picking_id.sale_id.invoice_ids.ids)
        current_user = picking_id.env.uid

        invoice_line_list = []
        for move_ids_without_package in picking_id.move_ids_without_package:
            vals = (0, 0, {
                'name': move_ids_without_package.description_picking,
                'product_id': move_ids_without_package.product_id.id,
                'price_unit': move_ids_without_package.product_id.lst_price,
                'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                'quantity': move_ids_without_package.product_uom_qty,
            })
            invoice_line_list.append(vals)
        self.env['account.move'].create({
            'move_type': 'out_refund',
            'invoice_origin': picking_id.name,
            'invoice_user_id': current_user,
            'narration': picking_id.name,
            'partner_id': picking_id.partner_id.id,
            'currency_id': picking_id.env.user.company_id.currency_id.id,
            'ref': _('Reversal for: %s') % self.reason if self.reason else '',
            'date': self.date or False,
            'invoice_date': self.date or False,
            'journal_id': self.journal_id and self.journal_id.id or moves[0].journal_id.id,
            'invoice_line_ids': invoice_line_list
        })

        ctx = dict(self.env.context)
        ctx.update({
            'default_partner_id': self.picking_id.partner_id.id,
            'search_default_picking_type_id': pick_type_id,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_late': False,
            'search_default_available': False,
        })
        return {
            'name': _('Returned Picking'),
            'view_mode': 'form,tree,calendar',
            'res_model': 'stock.picking',
            'res_id': new_picking_id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }
