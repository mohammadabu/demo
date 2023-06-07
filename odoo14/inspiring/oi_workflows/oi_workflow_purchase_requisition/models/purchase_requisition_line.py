'''
Created on Aug 19, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"
    
    state = fields.Selection(related='requisition_id.state', readonly = True)