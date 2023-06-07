from odoo import models, fields, api


class RecurringDocumentHistory(models.Model):
    _name = 'recurring.document.history'
    _description = 'Recurring Document History'
    
    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]
    
    subscription_id = fields.Many2one('recurring.document.subscription', 'Subscription', index=True, required=True, ondelete='cascade')
    document_ref = fields.Reference(
        string='Record', selection='_selection_target_model')
    document_deleted = fields.Boolean('Document Deleted')
    
