# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class AccountBankStatementLineHistory(models.Model):
    _name = "account.bank.statement.line.history"
    _description = "Bank Statement line History"
    
    
    date = fields.Date('Date')
    name = fields.Char(string='Label')
    partner_id = fields.Many2one('res.partner', string='Partner')
    ref = fields.Char(string='Reference')  
    currency_id = fields.Many2one('res.currency', string='Currency', help="The optional other currency if it is a multi-currency entry.") 
    cashier_appr_amt = fields.Monetary('Cashier amount')
    f_mgr_label = fields.Char('F-Mgr')
    factory_appr_amt = fields.Monetary('Factory Appr_Amt')
    ho_appr_amt = fields.Monetary('H/O Appr_Amt')
    statement_id = fields.Many2one('account.bank.statement', string='Statement', index=True, required=True, ondelete='cascade')
    amount = fields.Monetary(currency_field='currency_id')
    statement_approval_state = fields.Selection(related='statement_id.state_of_statement',string='Approval State',default="new")
    
