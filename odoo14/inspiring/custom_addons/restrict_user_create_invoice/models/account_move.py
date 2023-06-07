# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountMoveExt(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """
        Check If Invoice Amount is Greater than Order Amount then not allow to post invoice
        """
        order = self.env['sale.order'].search([('name', '=ilike', self.invoice_origin)])
        if self.move_type == 'out_invoice' and order and self.amount_total > order.amount_total:
            raise Warning("Invoice not Post, if Invoice amount is grater than Order Amount...!")

        return super(AccountMoveExt, self).action_post()
