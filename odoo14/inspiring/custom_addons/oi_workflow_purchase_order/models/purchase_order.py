'''
Created on Sep 18, 2018

@author: Zuhair Hammadi
'''
from odoo import models, api

class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ['approval.record', 'purchase.order']
    
    @api.model
    def _before_approval_states(self):
        return [('cancel', 'Cancelled'),('draft', 'RFQ'),('sent', 'RFQ Sent')]
    
    @api.model
    def _after_approval_states(self):
        return [('purchase', 'Purchase Order'), ('done', 'Locked'), ('rejected', 'Rejected')]    
            
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            order.action_approve()
        return True
    
    def button_cancel(self):
        self._remove_approval_activity()
        return super(PurchaseOrder, self).button_cancel()    
            
    def _on_approve(self):
        self.button_approve()