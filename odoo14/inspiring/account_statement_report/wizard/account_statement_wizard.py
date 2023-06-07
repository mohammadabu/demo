# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountStatement(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Account Statement'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    account_id = fields.Many2one('account.account', 'Account')

    def print_pdf(self):
        accounts = self.account_id or self.env['account.account'].search([])
        data = {'from_date': self.from_date, 'to_date': self.to_date, 'account_ids': accounts.ids}
        return self.env.ref('account_statement_report.account_statement_pdf').report_action(self, data=data)

    def print_xls(self):
        accounts = self.account_id or self.env['account.account'].search([])
        data = {'from_date': self.from_date, 'to_date': self.to_date, 'account_ids': accounts.ids}
        return self.env.ref('account_statement_report.account_statement_xls').with_context({'from_date': self.from_date, 'to_date': self.to_date}).report_action(accounts, data=data)
