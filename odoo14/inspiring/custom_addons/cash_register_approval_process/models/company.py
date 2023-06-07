# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class Company(models.Model):
    _inherit = "res.company"
    _description = "Company"
    
    pettycash_journal_id = fields.Many2one('account.journal',string='Petty Cash')
    
    
         
    
    