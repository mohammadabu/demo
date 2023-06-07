# -*- coding: utf-8 -*-

from odoo.tools.misc import xlwt
import io
import base64
from . import format_common
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class output_customer(models.TransientModel):
    _name = "customer.xlsx"

    name = fields.Char(string="Name")
    xls_output = fields.Binary(string="Excel Output", readonly=True)


class CustomerStatement(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    partner_ids = fields.Many2many('res.partner', string='Customers')
    account_type = fields.Selection([('receivable', 'Receivable'), ('payable', 'Payable'), ('both', 'Receivable and Payable')], default="both", required=True)
    aged_type = fields.Selection([('by_day', 'Age by Days'), ('by_month', 'Age by Months')], default="by_day", required=True)
    target_moves = fields.Selection(
        [('all_entries', 'All entries'),
         ('posted_only', 'Posted Only')], string='Target Moves',
        default='posted_only', required=True
    )

    def print_pdf(self):
        partners = self.env['res.partner']
        if self.partner_ids:
            for partner in self.partner_ids:
                partners |= partner
                partners |= partner.child_ids
        else:
            for partner in self.env['res.partner'].search([('parent_id', '=', False)]):
                partners |= partner
                partners |= partner.child_ids
        data = {'from_date': self.from_date, 'to_date': self.to_date, 'partner_ids': partners.ids,
                'account_type': self.account_type,'target_moves': self.target_moves, 'aged_type': self.aged_type}
        return self.env.ref('customer_statement_knk.customer_statement_pdf').report_action(self, data=data)

    def send_pdf(self):
        template = self.env.ref(
            'customer_statement_knk.email_template_edi_statement', False)
        partners = self.partner_ids or self.env['res.partner'].search([])
        for rec in partners:
            template.with_context(lang=rec.lang, from_date=self.from_date, to_date=self.to_date).send_mail(
                rec.id, force_send=True, raise_exception=True)

    def print_xls(self):
        partners = self.env['res.partner']
        if self.partner_ids:
            for partner in self.partner_ids:
                partners |= partner
                partners |= partner.child_ids
        else:
            for partner in self.env['res.partner'].search([('parent_id', '=', False)]):
                partners |= partner
                partners |= partner.child_ids
        workbook = xlwt.Workbook()
        # workbook.add_format({'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
        header_style = format_common.font_style(
            position="center", bold=1, fontos='black', font_height=220)
        value = format_common.font_style(position="center")
        value1 = format_common.font_style(
            position="center", bold=1, fontos='black')
        value2 = format_common.font_style(
            position="left", bold=1, fontos='black')
        value3 = format_common.font_style(
            position="center", bold=1, fontos='black')
        for partner in partners:
            sheet = workbook.add_sheet(partner.display_name)
            sheet.col(0).width = 4000
            sheet.col(1).width = 6000
            sheet.col(2).width = 6000
            sheet.col(3).width = 6000
            sheet.col(4).width = 6000
            sheet.col(5).width = 4000
            sheet.col(6).width = 4000
            sheet.col(7).width = 4000

            sheet.write_merge(0, 1, 3, 5, _(
                'Customer Statement'), header_style)
            sheet.write_merge(2, 2, 0, 0, _('Date From'), value3)
            sheet.write_merge(
                2, 2, 1, 1, self.from_date.strftime('%m/%d/%Y'), value)

            sheet.write_merge(3, 3, 0, 0, _('Date To'), value3)
            sheet.write_merge(
                3, 3, 1, 1, self.to_date.strftime('%m/%d/%Y'), value)

            sheet.write_merge(2, 2, 3, 3, _('Account Type'), value3)
            if self.account_type == 'receivable':
                sheet.write_merge(2, 2, 4, 4, _('Receivable'), value)
            elif self.account_type == 'payable':
                sheet.write_merge(2, 2, 4, 4, _('Payable'), value)
            else:
                sheet.write_merge(2, 2, 4, 4, _(
                    'Receivable and Payable'), value)

            sheet.write_merge(3, 3, 3, 3, _('Aged Type'), value3)
            if self.aged_type == 'by_day':
                sheet.write_merge(3, 3, 4, 4, _('Age by Days'), value)
            else:
                sheet.write_merge(3, 3, 4, 4, _('Age by Months'), value)

            address = partner.display_name + "\n" + \
                partner._display_address_knk().replace('\n\n', '\n')
            sheet.write_merge(2, 5, 6, 7, address, value1)

            sheet.write_merge(7, 7, 0, 0, _('Date'), value3)
            sheet.write_merge(7, 7, 1, 1, _('Journal'), value3)
            sheet.write_merge(7, 7, 2, 2, _('Account'), value3)
            sheet.write_merge(7, 7, 3, 3, _('Move'), value3)
            sheet.write_merge(7, 7, 4, 4, _('Reference'), value3)
            sheet.write_merge(7, 7, 5, 5, ('Debit'), value3)
            sheet.write_merge(7, 7, 6, 6, _('Credit'), value3)
            sheet.write_merge(8, 8, 2, 2, _('Opening Balance'), value1)
            sheet.write_merge(7, 7, 7, 7, _('Balance'), value3)

            opening_balance = partner.get_customer_opbalance(
                self.from_date, self.to_date, self.account_type)
            total_debit = 0.0
            total_credit = 0.0
            balance = 0.0
            if opening_balance['balance'] > 0:
                total_debit += opening_balance['balance']
                sheet.write_merge(
                    8, 8, 4, 4, opening_balance['balance'], value1)
            elif opening_balance['balance'] < 0:
                total_credit += opening_balance['balance']
                sheet.write_merge(
                    8, 8, 5, 5, opening_balance['balance'], value1)

            row = 9
            for stmt in partner.get_customer_statements(self.from_date, self.to_date, self.account_type):
                sheet.write_merge(
                    row, row, 0, 0, stmt.date.strftime('%m/%d/%Y'), value)
                sheet.write_merge(
                    row, row, 1, 1, stmt.move_id.journal_id.name, value)
                sheet.write_merge(
                    row, row, 2, 2, stmt.account_id.display_name, value)
                sheet.write_merge(row, row, 3, 3, stmt.move_id.name, value)
                sheet.write_merge(
                    row, row, 4, 4, stmt.move_id.ref or "-", value)
                sheet.write_merge(row, row, 5, 5, stmt.debit, value)
                sheet.write_merge(row, row, 6, 6, stmt.credit, value)
                balance += stmt.debit
                sheet.write_merge(row, row, 7, 7, balance, value)
                total_debit += stmt.debit
                total_credit += stmt.credit
                row += 1
            closing_bal = total_debit-total_credit
            sheet.write_merge(row, row, 2, 2, _("Closing Balance"), value1)
            if closing_bal < 0:
                sheet.write_merge(row, row, 4, 4, closing_bal, value1)
            elif closing_bal > 0:
                sheet.write_merge(row, row, 5, 5, closing_bal, value1)
            sheet.write_merge(row, row, 7, 7, balance, value1)

            row += 3
            agedheader = partner.get_agedheader(
                self.from_date, self.to_date, self.aged_type)
            sheet.write_merge(row, row, 1, 1, _("Not Due"), value1)
            sheet.write_merge(row, row, 2, 2, agedheader['4']['name'], value1)
            sheet.write_merge(row, row, 3, 3, agedheader['3']['name'], value1)
            sheet.write_merge(row, row, 4, 4, agedheader['2']['name'], value1)
            sheet.write_merge(row, row, 5, 5, agedheader['1']['name'], value1)
            sheet.write_merge(row, row, 6, 6, agedheader['0']['name'], value1)
            sheet.write_merge(row, row, 7, 7, _("Total"), value1)
            row += 1
            for ln in partner.get_ageddata(self.from_date, self.to_date, self.account_type, self.aged_type):
                if ln['partner_id'] == partner.id:
                    sheet.write_merge(row, row, 1, 1, ln['direction'], value1)
                    sheet.write_merge(row, row, 2, 2, ln['4'], value1)
                    sheet.write_merge(row, row, 3, 3, ln['3'], value1)
                    sheet.write_merge(row, row, 4, 4, ln['2'], value1)
                    sheet.write_merge(row, row, 5, 5, ln['1'], value1)
                    sheet.write_merge(row, row, 6, 6, ln['0'], value1)
                    sheet.write_merge(row, row, 7, 7, ln['total'], value1)
                    row += 1

        stream = io.BytesIO()
        workbook.save(stream)

        self.env.cr.execute(""" Delete from customer_xls """)
        attach_id = self.env['customer.xlsx'].create({'name': 'Customer Statement.xlsx',
                                                     'xls_output': base64.encodebytes(stream.getvalue())})

        return{
            'name': ('odoo'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'customer.xlsx',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
