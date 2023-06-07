# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class AccountPayment(models.Model):
    _inherit = "account.payment"
    _description = "Payment"
    
    account_bank_statement_id = fields.Many2one('account.bank.statement',string='Statement')
   
    def action_post(self):
        res = super(AccountPayment,self).action_post()
        for record in self:
            if record.account_bank_statement_id:
                record.account_bank_statement_id.write({'state_of_statement':'transferred'})
        return res        
    
    