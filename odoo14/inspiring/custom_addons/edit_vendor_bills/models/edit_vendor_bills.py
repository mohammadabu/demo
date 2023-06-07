from odoo import models, fields
class Edit_Vendor_Bills(models.Model):
    _inherit = 'account.move'
    bill_type = fields.Selection([('vendor', 'Vendor'), ('government', 'Government'), ('employee', 'Employee')])
    attachment = fields.Binary(string='Attachment')
    reference = fields.Char(
        string="Vendor Bill no.", help="The internal reference of the transaction", readonly=True,
        required=True)
    # partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
    #     states={'draft': [('readonly', False)]},
    #     check_company=True,
    #     string='Partner', change_default=True,
    #     domain="[('is_company', '=', 'True')]",)