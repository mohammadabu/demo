from odoo import models, fields


class RecurringDocumentConfig(models.Model):
    _name = 'recurring.document.config'
    _description = 'Recurring Document Config'
    
    name = fields.Char('Name')
    model_id = fields.Many2one('ir.model', 'Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    button_filter_domain = fields.Char('Hide Button Domain', required=True)
