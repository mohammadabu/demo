# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
import datetime
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_account_id = fields.Many2one(
        'partner.account',
        string='Partner Account Id'
        )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonly=True,
    )

    def unlink(self):
        self.ensure_one()
        return super(AccountMove, self).unlink()

class PartnerAccount(models.Model):
    _name = 'partner.account'
    _description = 'Partner Account'

    name = fields.Char(
        string='Name',
        copy=False,
        default=lambda self: _('New'),
    )
    start_date = fields.Date(
        string='Start date',
        required=True,
        help="Enter start date"
    )
    end_date = fields.Date(
        string='End date',
        required=True,
        default=fields.Date.today(),
        help="Enter end date"
    )
    partner_detail_ids = fields.One2many(
        string='Partner detail ids',
        comodel_name='partner.account.details',
        inverse_name='partner_account_id',
        domain=[('check','=',1)],
        context={},
    )
    partner_detail_in_ex_ids = fields.One2many(
        string='Partner detail ids',
        comodel_name='partner.account.details',
        inverse_name='partner_account_id',
        domain=[('check','=',2)],
        context={},
    )
    partner_detail_ass_li_ids = fields.One2many(
        string='Partner detail ids',
        comodel_name='partner.account.details',
        inverse_name='partner_account_id',
        domain=[('check','=',3)],
        context={},
    )
    partner_detail_bank_cash_ids = fields.One2many(
        string='Partner detail ids',
        comodel_name='partner.account.details',
        inverse_name='partner_account_id',
        domain=[('check','=',4)],
        context={},
    )
    partner_opning_bank_cash_ids = fields.One2many(
        string='Partner opning detail ids',
        comodel_name='partner.account.details',
        inverse_name='partner_account_id',
        domain=[('check','=',6)],
        context={},
    )
    opning_balance = fields.Boolean(
        string='Do You Want To Generat Opening Balance',
        help="Help to generat opening balance"
    )
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('posted', 'Posted'), ('done', 'Done'), ('cancel', 'Cancel')],
        default='draft',
    )
    opning_date = fields.Date(
        string='Opening Date',
        store=True,
    )
    partner_detail_payble_ids = fields.One2many(
        string='Partner detail ids',
        comodel_name='partner.account.details',
        inverse_name='partner_account_id',
        domain=[('check','=',5)],
    )
    opning_exp = fields.Float(
        string='Opnning Expenses',
        help='This is opning expenses'
    )
    opning_inc = fields.Float(
        string='Opning Income',
        help='This is opning income'
    )
    opning_exp_account_id = fields.Many2one(
        'account.account',
        string='Opning Expenses Account',
    )
    opning_inc_account_id = fields.Many2one(
        'account.account',
        string='Opning Income Account',
    )
    account_move_ids = fields.One2many(
        string='Account move ids',
        readonly=True,
        help=False,
        comodel_name='account.move',
        inverse_name='partner_account_id',
    )
    ad_account_id = fields.Many2one(
        string='Adjustment Account',
        comodel_name='account.account',
        domain=[],
    )
    ad_account = fields.Boolean(
        string='Ad Account Boolean',
        related='partner_opning_bank_cash_ids.check_partner',
    )
    journal_id = fields.Many2one(
        string='Journal',
        required=True,
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
    )
    inc_account_id = fields.Many2one(
        string='Opening Income Account',
        help="Select Adjustment Income Account",
        comodel_name='account.account',
        domain=[('internal_type','=','other'),('internal_group','in',['income',])],
    )
    exp_account_id = fields.Many2one(
        string='Opening Expences account',
        help=False,
        comodel_name='account.account',
        domain=[('internal_type','=','other'),('internal_group','in',['expense',])],
    )
    select_all_partner = fields.Boolean(
        string='Select all partner',
        help="It's help you to select all partner"
    )
    select_all_account = fields.Boolean(
        string='Select all account',
        help="It's help you to select all account"
    )

    @api.onchange('select_all_partner')
    def _onchange_select_all_partner(self):
        if self.select_all_partner == True:
            self.partner_detail_payble_ids.check_partner = True            
        if self.select_all_partner == False:
            self.partner_detail_payble_ids.check_partner = False            

    @api.onchange('select_all_account')
    def _onchange_select_all_account(self):
        if self.select_all_account == True:
            self.partner_opning_bank_cash_ids.check_partner = True            
        if self.select_all_account == False:
            self.partner_opning_bank_cash_ids.check_partner = False            


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('account.opning.balance') or _('New')
        result = super(PartnerAccount, self).create(vals)
        return result

    def unlink(self):
        try:
            for delete_id in self.account_move_ids:
                delete_id.write({'posted_before' : False, 'state' : 'draft'})
                delete_id.unlink()
            remove_ids = self.env['partner.account.details'].search([('partner_account_id','=',self.id)])
            self.write({'partner_detail_ids' : [(2, r.id) for r in remove_ids]})
            return super(PartnerAccount, self).unlink()
        except:
            raise UserError(_('You can not delete more than one record same time.\n Delete record one by one.'))


    @api.onchange('end_date')
    def _onchange_end_date(self):
        self.opning_date = self.end_date + datetime.timedelta(days=1)    


    def get_details(self):
                #============================= Receivable & Paybale ====================
        remove_ids = self.env['partner.account.details'].search([('partner_account_id','=',self.id)])
        self.write({'partner_detail_ids' : [(2, r.id) for r in remove_ids]})
        account_ids = self.env['account.account'].search([('internal_type', 'in',['receivable','payable'])])
        self.env.cr.execute("""
            SELECT line.account_id,
                   SUM(line.balance) AS balance,
                   SUM(line.debit) AS debit,
                   SUM(line.credit) AS credit
              FROM account_move_line line
              JOIN res_company comp ON comp.id = line.company_id
             WHERE line.date BETWEEN %(sart_date)s AND %(end_date)s AND line.account_id IN %(account_ids)s
             GROUP BY line.account_id
        """, {'sart_date' : self.start_date, 'end_date' : self.end_date, 'account_ids' : tuple(account_ids.ids)})
        results = self.env.cr.dictfetchall()
        data = {}
        for result in results:
            data['account_id'] = result['account_id']
            data['debit'] = result['debit']
            data['credit'] = result['credit']
            data['balance'] = result['balance']
            data['check'] = 1
            if result['balance']:
                self.write({'partner_detail_ids' : [(0,0, data)]})

        self.env.cr.execute("""
            SELECT line.partner_id,line.account_id,
                   SUM(line.balance) AS balance,
                   SUM(line.debit) AS debit,
                   SUM(line.credit) AS credit
              FROM account_move_line line
              JOIN res_company comp ON comp.id = line.company_id
             WHERE line.date BETWEEN %(sart_date)s AND %(end_date)s AND line.account_id IN %(account_ids)s
             GROUP BY line.partner_id, line.account_id
        """, {'sart_date' : self.start_date, 'end_date' : self.end_date, 'account_ids' : tuple(account_ids.ids)})
        results = self.env.cr.dictfetchall()
        data = {}
        for result in results:
            data['account_id'] = result['account_id']
            data['partner_id'] = result['partner_id']
            data['debit'] = result['debit']
            data['credit'] = result['credit']
            data['balance'] = result['balance']
            data['check'] = 1
            if result['balance']:
                self.write({'partner_detail_ids' : [(0,0, data)]})

                    #================================= Expense & Income =======================

        in_ex_ids = self.env['account.account'].search([('internal_type','=','other'),('internal_group','in',['expense','income'])])

        self.env.cr.execute("""
            SELECT line.account_id,
                   SUM(line.balance) AS balance,
                   SUM(line.debit) AS debit,
                   SUM(line.credit) AS credit
              FROM account_move_line line
              JOIN res_company comp ON comp.id = line.company_id
             WHERE line.date BETWEEN %(sart_date)s AND %(end_date)s AND line.account_id IN %(account_ids)s
             GROUP BY line.account_id
        """, {'sart_date' : self.start_date, 'end_date' : self.end_date, 'account_ids' : tuple(in_ex_ids.ids)})
        results = self.env.cr.dictfetchall()
        data = {}
        for result in results:
            data['account_id'] = result['account_id']
            data['debit'] = result['debit']
            data['credit'] = result['credit']
            data['balance'] = result['balance']
            data['check'] = 2
            self.write({'partner_detail_in_ex_ids' : [(0,0, data)]})

                    #=================================  Assets And Liability =======================

        ass_li_ids = self.env['account.account'].search([('internal_type','=','other'),('internal_group','in',['asset','liability'])])

        self.env.cr.execute("""
            SELECT line.account_id,
                   SUM(line.balance) AS balance,
                   SUM(line.debit) AS debit,
                   SUM(line.credit) AS credit
              FROM account_move_line line
              JOIN res_company comp ON comp.id = line.company_id
             WHERE line.date BETWEEN %(sart_date)s AND %(end_date)s AND line.account_id IN %(account_ids)s
             GROUP BY line.account_id
        """, {'sart_date' : self.start_date, 'end_date' : self.end_date, 'account_ids' : tuple(ass_li_ids.ids)})
        results = self.env.cr.dictfetchall()
        data = {}
        for result in results:
            data['account_id'] = result['account_id']
            data['debit'] = result['debit']
            data['credit'] = result['credit']
            data['balance'] = result['balance']
            data['check'] = 3
            self.write({'partner_detail_ass_li_ids' : [(0,0, data)]})

                    #==================================== Bank And Cash ==============================

        bank_cash_ids = self.env['account.account'].search([('internal_type','=','liquidity')])

        self.env.cr.execute("""
            SELECT line.account_id,
                   SUM(line.balance) AS balance,
                   SUM(line.debit) AS debit,
                   SUM(line.credit) AS credit
              FROM account_move_line line
              JOIN res_company comp ON comp.id = line.company_id
             WHERE line.date BETWEEN %(sart_date)s AND %(end_date)s AND line.account_id IN %(account_ids)s
             GROUP BY line.account_id
        """, {'sart_date' : self.start_date, 'end_date' : self.end_date, 'account_ids' : tuple(bank_cash_ids.ids)})
        results = self.env.cr.dictfetchall()
        data = {}
        for result in results:
            data['account_id'] = result['account_id']
            data['debit'] = result['debit']
            data['credit'] = result['credit']
            data['balance'] = result['balance']
            data['check'] = 4
            self.write({'partner_detail_bank_cash_ids' : [(0,0, data)]})

                    # ==================================== Partner Payble ================================

        payble_ids = self.env['partner.account.details'].search([('check','=',1),('partner_account_id','=',self.id)])
        new_data = {}
        payble_idss = payble_ids.filtered(lambda r : r.balance < 0 and r.account_id.internal_type == 'receivable')
        for payble_id in payble_idss:
            new_data['partner_id'] = payble_id.partner_id.id
            new_data['account_id'] = payble_id.account_id.id
            new_data['check'] = 5
            new_data['credit'] = abs(payble_id.balance)
            if payble_id.partner_id:
                self.write({'partner_detail_payble_ids' : [(0,0, new_data)]})
        new_data1 = {}
        payble_ids1 = payble_ids.filtered(lambda r : r.balance > 0 and r.account_id.internal_type == 'receivable')
        for payble_id1 in payble_ids1:
            new_data1['partner_id'] = payble_id1.partner_id.id
            new_data1['account_id'] = payble_id1.account_id.id
            new_data1['check'] = 5
            new_data1['debit'] = abs(payble_id1.balance)
            if payble_id1.partner_id:
                self.write({'partner_detail_payble_ids' : [(0,0, new_data1)]})

        receivable_idss = payble_ids.filtered(lambda r : r.balance < 0 and r.account_id.internal_type == 'payable')
        new_r_data = {}
        for receivable_id in receivable_idss:
            new_r_data['partner_id'] = receivable_id.partner_id.id
            new_r_data['account_id'] = receivable_id.account_id.id
            new_r_data['check'] = 5
            new_r_data['credit'] = abs(receivable_id.balance)
            if receivable_id.partner_id:
                self.write({'partner_detail_payble_ids' : [(0,0, new_r_data)]})
        new_r_data1 = {}
        receivable_ids1 = payble_ids.filtered(lambda r : r.balance > 0 and r.account_id.internal_type == 'payable')
        for receivable_id1 in receivable_ids1:
            new_r_data1['partner_id'] = receivable_id1.partner_id.id
            new_r_data1['account_id'] = receivable_id1.account_id.id
            new_r_data1['check'] = 5
            new_r_data1['debit'] = abs(receivable_id1.balance)
            if receivable_id1.partner_id:
                self.write({'partner_detail_payble_ids' : [(0,0, new_r_data1)]})

        opning_ex_ids = self.env['partner.account.details'].search([('partner_account_id','=',self.id),('check','=',5)])
        expenses = 0
        income = 0
        for opning_ex_id in opning_ex_ids:
            expenses += opning_ex_id.debit
            income += opning_ex_id.credit
        self.write({'opning_exp' : expenses, 'opning_inc' : income})

        #========================================= Opning Bank & Cash ==========================
        bank_ids = self.env['partner.account.details'].search([('check','=',4),('partner_account_id','=',self.id)])
        bank_idss = bank_ids.filtered(lambda r : r.balance < 0 and r.account_id.internal_type == 'liquidity')
        bank = dict()
        for bank_id in bank_idss:
            bank['account_id'] = bank_id.account_id.id
            bank['check'] = 6 
            bank['credit'] = abs(bank_id.balance) 
            self.write({'partner_opning_bank_cash_ids' : [(0,0, bank)]})

        bank_idss1 = bank_ids.filtered(lambda r : r.balance > 0 and r.account_id.internal_type == 'liquidity')
        bank_data1 = {}
        for bank_id in bank_idss1:
            bank_data1['account_id'] = bank_id.account_id.id
            bank_data1['check'] = 6 
            bank_data1['debit'] = abs(bank_id.balance) 
            self.write({'partner_opning_bank_cash_ids' : [(0,0, bank_data1)]})

        #=======================================================================================

    def action_post(self):
        if not self.opning_balance:
            raise UserError(_('Please Generate Opening Balance.')) 
        partner_ids = self.env['partner.account.details'].search([('check','=',5),('check_partner','=',True),('partner_account_id','=',self.id)])
        if not partner_ids:
            raise UserError(_('Please select partner for further process'))
        move_data = {}
        move_data1 = {}
        journal_id = self.journal_id.id
        for partner_id in partner_ids:
            if partner_id.account_id.internal_type == 'payable':
                if partner_id.debit:
                    line_line_data_cr = {
                        'name' : 'Opening Balance '+ partner_id.partner_id.name,
                        'account_id' : self.inc_account_id.id,
                        'partner_id' : partner_id.partner_id.id,
                        'credit' : partner_id.debit,
                    }
                    line_line_data_dr = {
                        'name' : 'Opening Balance '+ partner_id.partner_id.name,
                        'account_id' : partner_id.account_id.id,
                        'partner_id' : partner_id.partner_id.id,
                        'debit' : partner_id.debit,
                    }
                    move_data = {
                        'partner_id' : partner_id.partner_id.id,
                        'journal_id' :  journal_id,
                        'line_ids' : [(0,0, line_line_data_cr),(0,0, line_line_data_dr)],
                        'amount_total' : partner_id.credit,
                        'account_id' : partner_id.account_id.id,
                    }
                    new_move_id = self.env['account.move'].create(move_data)
                    self.write({'account_move_ids' : [(4,new_move_id.id)]})
                if partner_id.credit:
                    line_data_dr1 = {
                        'name' : 'Opening Balance '+partner_id.partner_id.name,
                        'account_id' : self.exp_account_id.id,
                        'partner_id' : partner_id.partner_id.id,
                        'debit' : partner_id.credit 
                    }
                    line_data_cr1 = {
                        'name' : 'Opening Balance '+partner_id.partner_id.name,
                        'account_id' : partner_id.account_id.id,
                        'partner_id' : partner_id.partner_id.id,
                        'credit' : partner_id.credit
                    }
                    move_data11 = {
                        'partner_id' : partner_id.partner_id.id,
                        'journal_id' :  journal_id,
                        'line_ids' : [(0,0, line_data_cr1),(0,0, line_data_dr1)],
                        'amount_total' : partner_id.debit,
                        'account_id' : partner_id.account_id.id,
                    }
                    new_move_id11 = self.env['account.move'].create(move_data11)
                    self.write({'account_move_ids' : [(4,new_move_id11.id)]})

            if partner_id.account_id.internal_type == 'receivable':
                if partner_id.credit:
                    line_data_dr2 = {
                        'name' : 'Opening Balance '+partner_id.partner_id.name,
                        'account_id' : partner_id.account_id.id,
                        'partner_id' : partner_id.partner_id.id,
                        'credit' : partner_id.credit 
                    }
                    line_data_cr2 = {
                        'name' : 'Opening Balance '+partner_id.partner_id.name,
                        'account_id' : self.exp_account_id.id,
                        'partner_id' : partner_id.partner_id.id,
                        'debit' : partner_id.credit
                    }
                    move_data1 = {
                        'partner_id' : partner_id.partner_id.id,
                        'journal_id' :  journal_id,
                        'line_ids' : [(0,0, line_data_cr2),(0,0, line_data_dr2)],
                        'amount_total' : partner_id.debit,
                        'account_id' : partner_id.account_id.id,
                    }
                    new_move_id1 = self.env['account.move'].create(move_data1)
                    self.write({'account_move_ids' : [(4,new_move_id1.id)]})
                if partner_id.debit:
                    line_line_data_cr2 = {
                        'name' : 'Opening Balance '+ partner_id.partner_id.name,
                        'account_id' : partner_id.account_id.id,
                        'partner_id' : partner_id.partner_id.id,
                        'debit' : partner_id.debit,
                    }
                    line_line_data_dr2 = {
                        'name' : 'Opening Balance '+ partner_id.partner_id.name,
                        'account_id' : self.inc_account_id.id,
                        'partner_id' : partner_id.partner_id.id,
                        'credit' : partner_id.debit,
                    }
                    move_data2= {
                        'partner_id' : partner_id.partner_id.id,
                        'journal_id' :  journal_id,
                        'line_ids' : [(0,0, line_line_data_cr2),(0,0, line_line_data_dr2)],
                        'amount_total' : partner_id.credit,
                        'account_id' : partner_id.account_id.id,
                    }
                    new_move_id2 = self.env['account.move'].create(move_data2)
                    self.write({'account_move_ids' : [(4,new_move_id2.id)]})

        # =========================================================== bank and cash ==========================================

        partner_bank_ids = self.env['partner.account.details'].search([('check','=',6),('check_partner','=',True),('partner_account_id','=',self.id)])
        # if not partner_bank_ids:
            # raise UserError(_('Please select bank and cash account for further process.'))
        journal_id = self.journal_id.id
        for partner_bank_id in partner_bank_ids:
            if partner_bank_id.account_id.internal_type == "liquidity":
                if partner_bank_id.credit:
                    bank_line_data_cr = {
                        'name' : 'Bank & Cash',
                        'account_id' : self.ad_account_id.id,
                        'debit' : partner_bank_id.credit,
                    }
                    bank_line_data_dr = {
                        'name' : 'Bank & Cash',
                        'account_id' : partner_bank_id.account_id.id,
                        'credit' : partner_bank_id.credit,
                    }
                    bank_move_data = {
                        'journal_id' :  journal_id,
                        'line_ids' : [(0,0, bank_line_data_cr),(0,0, bank_line_data_dr)],
                        'amount_total' : partner_bank_id.credit,
                        'account_id' : partner_bank_id.account_id.id,
                    }
                    bank_move_id = self.env['account.move'].create(bank_move_data)
                    self.write({'account_move_ids' : [(4,bank_move_id.id)]})

                if partner_bank_id.debit:
                    bank1_line_data_cr = {
                        'name' : 'Bank & Cash',
                        'account_id' : partner_bank_id.account_id.id,
                        'debit' : partner_bank_id.debit,
                    }
                    bank1_line_data_dr = {
                        'name' : 'Bank & Cash',
                        'account_id' : self.ad_account_id.id,
                        'credit' : partner_bank_id.debit,
                    }
                    bank1_move_data = {
                        'journal_id' : journal_id,
                        'line_ids' : [(0,0, bank1_line_data_cr),(0,0, bank1_line_data_dr)],
                        'amount_total' : partner_bank_id.debit,
                        'account_id' : partner_bank_id.account_id.id,
                    }
                    bank1_move_id = self.env['account.move'].create(bank1_move_data)
                    self.write({'account_move_ids' : [(4, bank1_move_id.id)]})

        # ============================================================================================================================

        self.write({'state' : 'posted'})


    def action_done(self):
        for account_move_id in self.account_move_ids:
            account_move_id.action_post()
        self.write({'state' : 'done'})

    def reverse_move(self):
        print('------------------------ this is reserve move')
        journal_id = self.journal_id.id
        for account_move_id in self.account_move_ids:
            print('--------------------------- account move id : ',account_move_id)
            vals = {
                'date_mode' : 'custom',
                'journal_id' : journal_id,
                'date' : fields.Date.today(),
                'move_ids' : [(4,account_move_id.id)],
            }
            reverse_id = self.env['account.move.reversal'].create(vals)
            reverse_id.reverse_moves()
            account_move_id.button_draft()
            account_move_id.with_context(force_delete=True).unlink()
        self.write({'state' : 'posted'})


class PartnerAccountDetails(models.Model):
    _name = 'partner.account.details'
    _description = 'Partner Account Details'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonly=True,
    )
    partner_account_id = fields.Many2one(
        string='Partner account id',
        comodel_name='partner.account',
        domain=[],
        context={},
    )
    credit = fields.Float(
        string='Credit',
    )
    debit = fields.Float(
        string='Debit',
    )
    balance = fields.Float(
        string='Balance',
    )
    check = fields.Integer(readonly=True,)
    check_partner = fields.Boolean(
        string='Select Partner',
        help='Select Partner For Opening Balance Entry'
    )

  