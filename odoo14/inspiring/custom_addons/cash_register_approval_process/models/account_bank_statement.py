# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError
from odoo.addons.account.wizard.pos_box import CashBox
from odoo.api import depends
from lxml import etree

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
    _description = "Bank Statement"
    
    
    @api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real')
    def _end_balance(self):
        for statement in self:
            statement.total_entry_encoding = sum([abs(line.amount) for line in statement.line_ids])
            statement.balance_end = statement.balance_start + statement.total_entry_encoding
            statement.difference = statement.balance_end_real - statement.balance_end

    
    
    
    def get_internal_transfer_entry(self):
        for record in self:
            record.count_internal_transfer_entry = 0.0
            record.confirmed_internal_transfer =False
            account_payment_ids = self.env['account.payment'].search([('account_bank_statement_id','=',record.id)])
            if account_payment_ids:
                record.count_internal_transfer_entry =  len(account_payment_ids.ids)
            
                for transfer in account_payment_ids:
                    if transfer.state =='posted': 
                        record.confirmed_internal_transfer = True
                        
                       
    state_of_statement = fields.Selection([('new','New'),('submitted','Submitted'),('first','First'),('final','Final'),('transferred','Transferred'),('validated','Validated')],string="State",default='new')
    head_office_comment = fields.Char('Head Office Comment')
    factory_manager_comment = fields.Char('Factory Manager Comment')
    current_user_group = fields.Boolean('User_group',compute="_set_current_user_group")
    is_factory_manager_comment = fields.Boolean('Is Factory Manager comment',compute="_set_current_user_group")
    is_cashier_group = fields.Boolean('Is Cashier',compute="_set_current_user_group",default=True)
    count_internal_transfer_entry = fields.Integer('Internal Transfer',compute="get_internal_transfer_entry",default=0)
    confirmed_internal_transfer = fields.Boolean('Confirmed Internal Transfer',compute="get_internal_transfer_entry",default=False)
    sr_no = fields.Char(string="Sr No", readonly=True, required=True, copy=False, default='New') 
    deleted_line_ids = fields.One2many('account.bank.statement.line.history', 'statement_id','Deleted Line', copy=False)
    
    
    def button_get_internal_transfer(self):
        account_payment_ids = self.env['account.payment'].search([('account_bank_statement_id','=',self.id)])
        if account_payment_ids: 
            return {
                'name': _('Internal Transfer Entries'),
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', account_payment_ids.ids)],
            }
        return True     
                
    def set_status_to_submit(self):
        for record in self:
            record.write({'state_of_statement': 'submitted'})
            
    def set_status_to_final_approval(self):
        for record in self:
            record.write({'state_of_statement': 'final','balance_end_real':record.balance_end})
            record.button_post()        
    
        
    def _set_current_user_group(self):
        user_in_group_1 = self.env.user.has_group('cash_register_approval_process.group_final_approval_cash_register')
        user_in_group_2 = self.env.user.has_group('cash_register_approval_process.group_first_approval_cash_entries')
        user_in_group_3 = self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry')
        
        for record in self:
            record.current_user_group = user_in_group_1
            record.is_factory_manager_comment = user_in_group_2
            record.is_cashier_group = user_in_group_3
    
    def check_confirm_bank(self):
        if not self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry'):
            raise UserError(_("No Authorization"))
        return super(AccountBankStatement,self).check_confirm_bank()
        

    def set_state_to_first_approval(self):
        if not self.env.user.has_group('cash_register_approval_process.group_first_approval_cash_entries'):
            if self.env.user.has_group('cash_register_approval_process.group_final_approval_cash_register'):
                raise UserError(_("No Authorization"))
            if self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry'):
                raise UserError(_("Pending for approval by next authority"))
        for record in self:
            record.write({'state_of_statement':'first'})
    
    
    def action_bank_reconcile_bank_statements(self):
        if not self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry'):
            raise UserError(_("No Authorize"))
        res = super(AccountBankStatement,self).action_bank_reconcile_bank_statements()
        return res
    
    @api.model
    def return_to_bank_statement(self,bank_statement_id):
        if bank_statement_id:
            bank_st_id = self.browse(bank_statement_id[0].get('id')) or False
            if bank_st_id:
                bank_st_id.write({'state_of_statement':'new'})
        return        
        
    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountBankStatement, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            is_user_in_group_1 = self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry')
            if not is_user_in_group_1:
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//field[@name='line_ids']/tree"):
                    node.set('create', 'false')
                res['arch'] = etree.tostring(doc)
        return res
    
    def write(self,vals):
        res = super(AccountBankStatement,self).write(vals)
        return res
        
    
    def set_statement_ending_balance(self):
        for statement in self:
            total_entry_encoding = 0.0 
            approved_statement_lines = statement.line_ids.filtered(lambda m: m.is_approved)
            total_entry_encoding = sum([line.amount for line in approved_statement_lines])
            statement.write({'balance_end_real':statement.balance_start + total_entry_encoding})
            
    
    @api.model
    def create(self, vals):
        if not self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry'):
            raise UserError(_("No Authorization"))
        if self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry'):
            if 'line_ids' in vals:
                for line in vals['line_ids']:
                    if line[2].get('factory_appr_amt') or line[2].get('is_approved') or line[2].get('f_mgr_label'):
                        raise UserError(_("No Authorization"))
        
        if vals.get('sr_no', 'New') == 'New':
            vals['sr_no'] = self.env['ir.sequence'].next_by_code('cash.request.sequence') or 'New'            
        return super(AccountBankStatement,self).create(vals)    
    
    def set_internal_transfer_entry(self):
        action_data =  {
                'name': _('Internal Transfer Entries'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'account.payment',
                'view_id': False,
                'type': 'ir.actions.act_window',
                
            }
        for statement in self:
            internal_transfer_ids =  self.env['account.payment'].search([('account_bank_statement_id','=',self.id)],limit=1)
            if internal_transfer_ids:
                action_data.update({'res_id':internal_transfer_ids.id,'context':{'skip_amount_compute':True}})
            else:
                amount = 0.0 
                for stat_line in statement.line_ids:
                    amount +=  stat_line.amount
                      
                context = {'default_destination_journal_id':statement.journal_id.id,
                       'default_currency_id':self.env.user.company_id.currency_id.id,
                       'default_amount':abs(amount),
                       'default_account_bank_statement_id':statement.id,
                       'default_is_internal_transfer':True,
                       'default_journal_id':self.env.user.company_id and self.env.user.company_id.pettycash_journal_id.id or False,
                       'skip_amount_compute':True}
                
                action_data.update({'context':context})
                
        return action_data
            
    
class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'
    _description = 'Account Reconciliation widget'
      
    @api.model
    def process_bank_statement_line(self, st_line_ids, data):
        if not self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry'):
            raise UserError(_("Pending for approval by next authority"))
        st_lines = self.env['account.bank.statement.line'].browse(st_line_ids)
        res = super(AccountReconciliation,self).process_bank_statement_line(st_line_ids,data)
        for st_line in st_lines:
            st_line.statement_id.write({'state_of_statement':'validated'})
        return res

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"
    _description = "Bank Statement line"
    
    @depends('statement_approval_state')
    def _check_approval_group(self):
        user_in_group_1 = self.env.user.has_group('cash_register_approval_process.group_only_create_cash_register_entry')
        user_in_group_2 = self.env.user.has_group('cash_register_approval_process.group_first_approval_cash_entries')
        user_in_group_3 = self.env.user.has_group('cash_register_approval_process.group_final_approval_cash_register')
        user_in_group_4 = self.env.user.has_group('cash_register_approval_process.group_user_internal_transfer')
        
        for record in self:
            record.is_in_group_1 = user_in_group_1
            record.is_in_group_2 = user_in_group_2
            record.is_in_group_3 = user_in_group_3
            record.is_in_group_4 = user_in_group_4
            
            set_amount_readonly = False
            if record.statement_approval_state == 'submitted' and user_in_group_1:
                set_amount_readonly = True
            if record.statement_approval_state == 'first' and user_in_group_2:
                set_amount_readonly = True
            if record.statement_approval_state == 'final' and user_in_group_3:
                set_amount_readonly = True
            if record.statement_approval_state == 'final' and user_in_group_4:
                set_amount_readonly = True
            record.set_amount_readonly = set_amount_readonly
    
        
    f_mgr_label = fields.Char('F-Mgr')
    factory_appr_amt = fields.Monetary('Factory Appr_Amt')
    cashier_appr_amt = fields.Monetary('Cashier amount')
    ho_appr_amt = fields.Monetary('H/O Appr_Amt')
    is_approved = fields.Boolean('Is approved')
    is_in_group_1 = fields.Boolean(compute='_check_approval_group',string='Is in Group 1')
    is_in_group_2 = fields.Boolean(compute='_check_approval_group',string='Is in Group 2')
    is_in_group_3 = fields.Boolean(compute='_check_approval_group',string='Is in Group 3')
    is_in_group_4 = fields.Boolean(compute='_check_approval_group',string='Is in Group 4')
    statement_approval_state = fields.Selection(related='statement_id.state_of_statement',string='Approval State',default="new")
    journal_type = fields.Selection(related='journal_id.type', help="Technical field used for usability purposes")
    set_amount_readonly = fields.Boolean(compute='_check_approval_group',string='Set amount column readonly')
    
    def write(self,vals):
        res = super(AccountBankStatementLine,self).write(vals)
        for record in self:
            if record.is_in_group_2 or record.is_in_group_3 or record.is_in_group_4:
                if 'amount' in vals and record.cashier_appr_amt:
                    if abs(vals.get('amount')) > record.cashier_appr_amt:
                        raise UserError(_("You can not insert the amount greater than the cashier request amount."))     
        return res
    
    
    def unlink(self):
        for line_id in self:
            line_dict = {'date':line_id.date or False,
                         'name':line_id.name or '',
                         'partner_id':line_id.partner_id and line_id.partner_id.id or False,
                         'ref':line_id.ref or '',
                         'cashier_appr_amt' : line_id.cashier_appr_amt or 0.0,
                         'f_mgr_label':line_id.f_mgr_label or '',
                         'factory_appr_amt':line_id.factory_appr_amt or 0.0,
                         'ho_appr_amt':line_id.ho_appr_amt or 0.0,
                         'amount':line_id.amount or 0.0,
                         'statement_id': line_id.statement_id and line_id.statement_id.id or False,
                        }
            self.env['account.bank.statement.line.history'].create(line_dict)
        return super(AccountBankStatementLine, self).unlink()
   
        
class CashBoxOut(CashBox):
    _inherit = 'cash.box.out'
    
    def _create_bank_statement_line(self, record):
        for box in self:
            if record.state == 'confirm':
                raise UserError(_("You cannot put/take money in/out for a bank statement which is closed."))
            values = box._calculate_values_for_statement_line(record)
            record.with_context(skip_line_validity=True).write({'line_ids': [(0, False, values)]})     


    


