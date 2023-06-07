from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)
class Edit_Vendor_Bills_States(models.Model):
    _inherit = 'account.move'
    state = fields.Selection([('draft', 'Draft'), ('manager_approval', 'Manager approval'), ('accounting', 'Accounting'), ('head_of_accounting', 'Head of accounting'), ('posted', 'Posted'), ('cancel', 'Cancelled')])
    #state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled')])
    emp_has_permission = fields.Selection([('yes', 'yes'),('no', 'no') ], compute='_compute_emp_has_permission')
    employee = fields.Many2one('hr.employee')
    def manager_approval_state(self):
        self.state = 'manager_approval'

    def accounting_state(self):
        self.state = 'accounting'

    def head_of_accounting_state(self):
        self.state = 'head_of_accounting'

    #def manager_approval_state_123(self):
    #    self.state = 'draft'

    states_type = fields.Selection(
        [('stand', 'standard'), ('ven', 'vendor'), ('gov', 'government'), ('emp', 'employee')]
        , compute='_compute_states_type')
    stand_states = fields.Selection(related='state')
    ven_states = fields.Selection(related='state')
    gov_states = fields.Selection(related='state')
    emp_states = fields.Selection(related='state')
    @api.depends('state')
    def _compute_emp_has_permission(self):
        creation_user = self.create_uid
        position = ''
        self.emp_has_permission = 'no'
        if self.state == 'draft':
            if creation_user.id == self.env.user.id:
                self.emp_has_permission = 'yes'
            else:
                self.emp_has_permission = 'no'
        elif self.state == 'posted' or self.state == 'cancel':
            self.emp_has_permission = 'no'
            
        elif self.state == 'manager_approval' and self.move_type == 'in_invoice':
            position = 'general_manager'
        elif self.state == 'accounting' and self.move_type == 'in_invoice':
            position = 'accountant'
        elif self.state == 'head_of_accounting' and self.move_type == 'in_invoice':
            position = 'senior_accountant'

        if position:
            position_info = self.env['hr.job'].sudo().search([('internal_id', '=', position)])
            employees = self.env['hr.employee'].sudo().search([('job_id', '=', position_info[0].id), ('user_id', '=', self.env.user.id)])
            if not employees:
                self.emp_has_permission = 'no'
            else:
                self.emp_has_permission = 'yes'

        #self.state = 'draft'

    @api.depends('state')
    def _compute_states_type(self):
        invoice_type = self.move_type
        self.states_type = 'stand'
        if invoice_type == 'in_invoice':
            if self.bill_type == 'vendor':
                self.states_type = 'ven'
            elif self.bill_type == 'government':
                self.states_type = 'gov'
            else:
                self.states_type = 'emp'


