# -*- coding: utf-8 -*-
from odoo import models

class AccountAccount(models.Model):
    _inherit = "account.account"

    def get_move_lines(self, from_date, to_date):
        domain = [('account_id', '=', self.id)]
        if from_date and to_date:
            domain += [('date', '>=', from_date), ('date', '<=', to_date)]
        return self.env['account.move.line'].search(domain, order='date')
