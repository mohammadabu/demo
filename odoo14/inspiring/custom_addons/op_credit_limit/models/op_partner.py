# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.
#      Copying is not allowed.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cr=fields.Char(string='Commercial Registry', )

    set_credit_limit = fields.Boolean(
        string='Set Credit Limit?'
    )

    credit_limit = fields.Float(
        string='Credit Limit'
    )

    hold_credit_limit = fields.Boolean(
        string='Allow Over Credit Limit?'
    )

    cr_balance = fields.Monetary(compute="get_existing_credit_standing", string="Current Balance",)
    
    debit = fields.Monetary(string="Current debit")
    credit = fields.Monetary(string="Current Credit")

    # get up to date debit credit and balance
    def get_existing_credit_standing(self):
        self.ensure_one()
        table = self.env['account.move.line'].search([
            ('full_reconcile_id', '=', False),
            ('account_id.user_type_id.name', 'in', ['Receivable', 'Payable']),
        ])
        balance = 0.0
        debit = 0.0
        credit = 0.0
        for record in table:
            if record.partner_id.id == self.id:
                balance += record.balance
                debit += record.debit
                credit += record.credit
            self.cr_balance = balance
            self.debit = debit
            self.credit = credit
        return self.cr_balance, self.debit, self.credit


    #to open credit request in smart button

    def open_credit_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': ('Credit Request'),
            'view_mode': 'tree,form',
            'res_model': 'credit.request',
            # 'target': 'new',
            'domain': [('partner_id', '=', self.id),
                    #    ('state', '!=', 'draft')
                       ],
            # 'context': "{create': True,'edit': False ,'True': True }",
            
        }

    credit_request_count = fields.Integer(compute='_compute_credit_request_count', )

    def _compute_credit_request_count(self):
        credit_requests = self.env['credit.request']
        for partner in self:
            current_balance = 0
            credit_ids = credit_requests.search([('partner_id', '=', partner.id), ('state', '=', 'done')])
            if credit_ids:
                for credit in credit_ids:
                    current_balance += credit.credit_limit

            partner.credit_request_count = current_balance
