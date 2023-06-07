# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models ,SUPERUSER_ID
from odoo.exceptions import UserError

class SaleQwebReport(models.AbstractModel):

    _name = 'report.sales_margin_report_omax.report_sale_margin_omax'
    _description = 'Sales Margin PDF Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        data = data if data is not None else {}
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        if docs.company_ids:
            company_ids = docs.company_ids
        else:
            company_ids = self.env["res.company"].search([])
        if docs.user_ids:
            user_ids = docs.user_ids
        else:
            user_ids = self.env["res.users"].search([])

        user_ids_lst = []
        if user_ids:
            user_ids_lst = user_ids.ids

        company_id_lst = []
        if company_ids:
            company_id_lst = company_ids.ids

        sale_orders = self.env['sale.order'].search([
            ('user_id', 'in', user_ids_lst),
            ('company_id', 'in', company_id_lst),
            ('date_order', '>=', str(docs.start_date)),
            ('date_order', '<=', str(docs.end_date)),
            ('state', 'in', ('done','sale'))])

        return {
            'doc_ids': self.ids,
            'doc_model': 'model',
            'docs': docs,
            'data': data,
            'sale_orders': sale_orders,
        }
