from odoo import models,fields,api

class RecurringDocumentField(models.Model):
    _name='recurring.document.field'
    _description='Recurring Document Fields'
    
    subscription_id = fields.Many2one('recurring.document.subscription', 'Subscription')
    field = fields.Many2one('ir.model.fields', domain="[('model_id', '=', parent.model)]", required=True, ondelete='cascade')
    value = fields.Selection([('false', 'False'), ('date', 'Current Date')], string='Default Value', help="Default value is considered for field when new document is generated.")