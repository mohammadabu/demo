from odoo import models, fields, api
class Edit_Expenses(models.Model):
    _inherit = 'hr.expense'
    po_number = fields.Char(string='PO Number', required=True)
    po_file = fields.Binary(string='PO File', required=True)