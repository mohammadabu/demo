from odoo import fields, models

class Edit_Company(models.Model):
    _inherit = 'res.company'
    po_box = fields.Char(string='P.O. Box')