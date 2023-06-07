# -*- coding: utf-8 -*-
# License: Odoo Proprietary License v1.0

from odoo import fields, models, api, _


class AccountReportFinancial(models.TransientModel):
    _inherit = "financial.report"

    def view_report_pdf(self):
        if self._context.get('excel_report'):
            self.ensure_one()
            data = dict()
            data['ids'] = self.env.context.get('active_ids', [])
            data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
            data['form'] = self.read(
                ['date_from', 'enable_filter', 'debit_credit', 'date_to',
                 'account_report_id', 'target_move', 'view_format',
                 'company_id'])[0]
            used_context = self._build_contexts(data)
            data['form']['used_context'] = dict(
                used_context,
                lang=self.env.context.get('lang') or 'en_US')

            report_lines = self.get_account_lines(data['form'])
            # find the journal items of these accounts
            journal_items = self.find_journal_items(report_lines, data['form'])

            def set_report_level(rec):
                """This function is used to set the level of each item.
                This level will be used to set the alignment in the dynamic reports."""
                level = 1
                if not rec['parent']:
                    return level
                else:
                    for line in report_lines:
                        key = 'a_id' if line['type'] == 'account' else 'id'
                        if line[key] == rec['parent']:
                            return level + set_report_level(line)

            # finding the root
            for item in report_lines:
                item['balance'] = round(item['balance'], 2)
                if not item['parent']:
                    item['level'] = 1
                    parent = item
                    report_name = item['name']
                    id = item['id']
                    report_id = item['r_id']
                else:
                    item['level'] = set_report_level(item)
            currency = self._get_currency()
            data['currency'] = currency
            data['journal_items'] = journal_items
            data['report_lines'] = report_lines
            # checking view type
            return self.env.ref('accounting_excel_reports.action_report_financial_excel').report_action(
                self, data=data, config=False)
        else:
            return super(AccountReportFinancial, self).view_report_pdf()
