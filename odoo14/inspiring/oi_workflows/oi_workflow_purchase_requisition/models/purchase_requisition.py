'''
Created on Oct 3, 2018

@author: Admin
'''
from odoo import models, api, fields

class PurchaseRequisition(models.Model):
    _name = "purchase.requisition"
    _inherit = ['approval.record', 'purchase.requisition', 'mail.activity.mixin']        

    state_blanket_order = fields.Selection(lambda self : self._get_state())
        
    @api.model
    def _before_approval_states(self):
        return [('draft', 'Draft')]
    
    @api.model
    def _after_approval_states(self):
        return [('in_progress', 'Confirmed'), ('open', 'Bid Selection'), ('done', 'Done'), ('cancel', 'Cancelled'), ('rejected', 'Rejected')]    
          
    def button_cancel(self):
        self._remove_approval_activity()
        return super(PurchaseRequisition, self).button_cancel()    
            
    def _on_approve(self):
        self.action_in_progress()
        
    def _on_cancel(self):
        return 'cancel'
        
        