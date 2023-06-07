from odoo import models,fields,api

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['recurring.document','account.move']