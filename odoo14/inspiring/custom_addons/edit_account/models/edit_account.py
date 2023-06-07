from socket import timeout

from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings





from gevent import Timeout
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
class Edit_Account(models.Model):
    _inherit = "account.journal"
    def create_other_payment(self):
        """return action to create a internal transfer"""
        return self.open_payments_action('transfer', mode='form')

class Edit_Account_Form(models.Model):
    _inherit = 'account.move'
    sale_order = fields.Many2one('sale.order')
    check = fields.Boolean(compute = "check_invoice_status")

    @api.depends('check')
    def check_invoice_status(self):
        if  self.posted_before == True and self.state in ('draft','posted'):
            self.check=True
        else:
            self.check=False

    @api.onchange('partner_id')
    def _onchange_partner_id_set_invoice_payment_term_id(self):
        _logger.info('self.partner_id %s', self.partner_id)
        if self.partner_id:
            if self.partner_id.property_payment_term_id:
                self.invoice_payment_term_id = self.partner_id.property_payment_term_id
            else:
                self.invoice_payment_term_id = False
        

class Edit_Sale_order(models.Model):
    _inherit = 'sale.order'
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).', self.company_id.name, self.company_id.id))

        _logger.info('hello from this side invoice_vals')
        _logger.info('self_val %s', self)
        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_id.id, # edited
            'sale_order': self.id, # added new
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals

class Edit_Sale_Advance_Payment(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        _logger.info('hello from this side')
        _logger.info('order_id %s', order.id)
        if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))

        amount, name = self._get_advance_details(order)

        invoice_vals = self._prepare_invoice_values(order, name, amount, so_line)

        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id

        invoice_vals['sale_order'] = order.id

        invoice = self.env['account.move'].with_company(order.company_id).sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice, 'origin': order},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

class Account_Sequance_Change(models.Model):
    #_name = 'account.sequance.change'
    _inherit = 'account.move'

    # @api.model
    # def _get_starting_sequence(self):
    #     _logger.info('hello hello hello')
    #     self.ensure_one()
    #     first_part = self.journal_id.code
    #     if self.move_type == 'out_refund':
    #         first_part = 'CN'
    #     starting_sequence = "%s/%04d/%02d/0000" % (first_part, self.date.year, self.date.month)
    #     if self.journal_id.refund_sequence and self.move_type in ('out_refund', 'in_refund'):
    #         starting_sequence = "R" + starting_sequence
    #     return starting_sequence 


    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        def journal_key(move):
            return (move.journal_id, move.journal_id.refund_sequence and move.move_type)

        def date_key(move):
            return (move.date.year, move.date.month)

        grouped = defaultdict(  # key: journal_id, move_type
            lambda: defaultdict(  # key: first adjacent (date.year, date.month)
                lambda: {
                    'records': self.env['account.move'],
                    'format': False,
                    'format_values': False,
                    'reset': False
                }
            )
        )
        self = self.sorted(lambda m: (m.date, m.ref or '', m.id))
        highest_name = self[0]._get_last_sequence() if self else False
        # Group the moves by journal and month
        for move in self:
            if not highest_name and move == self[0] and not move.posted_before and move.date:
                # In the form view, we need to compute a default sequence so that the user can edit
                # it. We only check the first move as an approximation (enough for new in form view)
                pass
            elif (move.name and move.name != '/') or move.state != 'posted':
                try:
                    if not move.posted_before:
                        move._constrains_date_sequence()
                    # Has already a name or is not posted, we don't add to a batch
                    continue
                except ValidationError:
                    # Has never been posted and the name doesn't match the date: recompute it
                    pass
            group = grouped[journal_key(move)][date_key(move)]
            if not group['records']:
                # Compute all the values needed to sequence this whole group
                move._set_next_sequence()
                group['format'], group['format_values'] = move._get_sequence_format_param(move.name)
                group['reset'] = move._deduce_sequence_number_reset(move.name)
            group['records'] += move
        # Fusion the groups depending on the sequence reset and the format used because `seq` is
        # the same counter for multiple groups that might be spread in multiple months.
        final_batches = []
        for journal_group in grouped.values():
            journal_group_changed = True
            for date_group in journal_group.values():
                if (
                    journal_group_changed
                    or final_batches[-1]['format'] != date_group['format']
                    or dict(final_batches[-1]['format_values'], seq=0) != dict(date_group['format_values'], seq=0)
                ):
                    final_batches += [date_group]
                    journal_group_changed = False
                elif date_group['reset'] == 'never':
                    final_batches[-1]['records'] += date_group['records']
                elif (
                    date_group['reset'] == 'year'
                    and final_batches[-1]['records'][0].date.year == date_group['records'][0].date.year
                ):
                    final_batches[-1]['records'] += date_group['records']
                else:
                    final_batches += [date_group]
        # Give the name based on previously computed values
        for batch in final_batches:
            for move in batch['records']:
                if move.move_type == 'out_refund':
                    batch['format_values']['prefix1'] = 'CN/'
                move.name = batch['format'].format(**batch['format_values'])
                batch['format_values']['seq'] += 1
            batch['records']._compute_split_sequence()

        self.filtered(lambda m: not m.name).name = '/'        


class AccountPaymentEditt(models.Model):
    _inherit = 'account.payment'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer/Vendor",
        store=True, readonly=False, ondelete='restrict',
        compute='_compute_partner_id',
        domain="[]",
        tracking=True)