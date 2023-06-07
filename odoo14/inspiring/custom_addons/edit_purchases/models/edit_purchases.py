from odoo import models, fields
class Edit_Purchases(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, 
        states=READONLY_STATES, change_default=True, tracking=True, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('is_company', '=', 'True')]", 
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
        
class EditPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit = fields.Float(string='Estimate Price', required=True, digits='Product Price')
