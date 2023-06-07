# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import time

from dateutil.relativedelta import relativedelta

from odoo import fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountAgedTrialBalanceNew(models.TransientModel): 
    _name = 'account.aged.trial.balance.new'
    _inherit = 'account.common.partner.report'
    _description = 'Account Aged Trial balance Report'

    journal_ids = fields.Many2many('account.journal', string='Journals',
                                   required=True)
    period_length = fields.Integer(string='Period Length (days)',
                                   required=True, default=30)
    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d')) 

    partner_id = fields.Many2one('res.partner',default=lambda self: self.env.context.get('id'))

    def print_account_aged_balance(self):
        # project_id = fields.Many2one('project.project',default=lambda self: self.env.context.get('project_id'))
        data = {
            'journal_ids': self.journal_ids,
            'period_length':self.period_length,
            'date_from': self.date_from,
            'partner_id':self.partner_id
        }
        return self.env.ref('base_accounting_kit.action_report_print_account_aged_balance').report_action(self, data=data)
        # _logger.info("print_account_aged_balance")
        # _logger.info(self.env.context.get('id')) 
