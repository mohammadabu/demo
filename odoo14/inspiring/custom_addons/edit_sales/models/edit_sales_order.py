from odoo import SUPERUSER_ID, api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class Edit_Sales_Fields(models.Model):
    _inherit = "sale.order"
    _description = "Sales Order"
    deadline_date = fields.Date(string='Deadline')
    po_number = fields.Char(string='PO Number', index=True, store=True)
    po_file = fields.Binary(string='PO File')
    po_is_required = fields.Boolean(compute='compute_is_po_required')
    same_po_order_id = fields.Many2one('sale.order', string='Sale Order with same Po Number', readonly=True, store=False)
    deliveiry_address = fields.Many2one(
        'res.partner', string='Deliveiry Address', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|',('company_id', '=', company_id), ('parent_id', '=', partner_id), ('type', '=', 'delivery')]",)

    # check_position = fields.Boolean(compute='check_user_group_position')

    # # to check the user group position, this procedure will be used to hid create, create and ecit for spicific group position.
    # @api.depends('partner_id')
    # def check_user_group_position(self):
    #     uid = request.session.uid
    #     user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
    #     if user.has_group('sales_team.group_sale_manager'):
    #         _logger.info('==========================>> False')
    #         self.check_position = False
    #     else:
    #         _logger.info('==========================>> True')
    #         self.check_position = True

    @api.onchange('po_number')
    def _compute_same_po_order_id(self):
        if self.po_number:
            product = self.env['sale.order'].sudo().search([('po_number', '=', self.po_number)], limit=1)                    
            if product:
                self.same_po_order_id = product.id
            else:
                self.same_po_order_id = False
        return

    def compute_is_po_required(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        position = self.env['hr.job'].sudo().search([('id', '=', employee.job_id.id)], limit=1)
        user = self.env['res.users'].sudo().search([('id', '=', self.env.user.id)], limit=1)
        _logger.info('position info id %s', position.id)
        _logger.info('position internal_id %s', position.internal_id)
        _logger.info('user has_group %s', user.has_group('sales_team.group_sale_manager'))
        if position.internal_id == 'sales_manager' or user.has_group('sales_team.group_sale_manager'):
            self.po_is_required = False
        else:
            self.po_is_required = True

    @api.onchange('partner_id')
    def check_po_is_required(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        position = self.env['hr.job'].sudo().search([('id', '=', employee.job_id.id)], limit=1)
        user = self.env['res.users'].sudo().search([('id', '=', self.env.user.id)], limit=1)
        self.deliveiry_address = False
        if position.internal_id == 'sales_manager' or user.has_group('sales_team.group_sale_manager'):
            self.po_is_required = False
        else:
            self.po_is_required = True

    def action_confirm(self):
        res = super(Edit_Sales_Fields, self).action_confirm()
        order_ref_id = str(self.name)
        wh_out_picking = self.env['stock.picking'].sudo().search([('origin', '=', order_ref_id)], limit=1)
        wh_out_picking.write({'sale_deadline_date': self.deadline_date})
        if (self.delivery_status == 'pick_up'):
            wh_out_picking.write({'is_pickup': True})
            wh_out_picking.write({'delivery_status': 'pick_up'})
        else:
            wh_out_picking.write({'is_pickup': False})
        return res

    @api.model
    def write(self, vals):
        res = super(Edit_Sales_Fields, self).write(vals)
        order_ref_id = str(self.name)
        wh_out_picking = self.env['stock.picking'].sudo().search([('origin', '=', order_ref_id)], limit=1)
        wh_out_picking.write({'sale_deadline_date': self.deadline_date})
        if (self.delivery_status == 'pick_up'):
            wh_out_picking.write({'is_pickup': True})
            wh_out_picking.write({'delivery_status': 'pick_up'})
        else:
            wh_out_picking.write({'is_pickup': False})
        return res

    def action_compute_lines(self):
        for order in self:
            for sale_line in order.order_line:
                if (sale_line.qty_delivered < sale_line.product_uom_qty and order.state in ['sale', 'done']):
                    sale_line.is_qty_delivered_less = False
                    sale_line.qty_delivered_is_less = "Quantity Delivered Is Less than Quantity Ordered"
                else:
                    sale_line.qty_delivered_is_less = " "
                    sale_line.is_qty_delivered_less = True
    

class Edit_Stock_Picking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"
    is_pickup = fields.Boolean()
    delivery_status = fields.Selection(selection=[
        ('pick_up', 'Pick Up'),
    ], string='Delivery Status', readonly=True)
    sale_deadline_date = fields.Date(string='Deadline', readonly=True)
    date_deadline = fields.Datetime(
        "Expiration", compute='_compute_date_deadline', store=True,
        help="Date Promise to the customer on the top level document (SO/PO)")
