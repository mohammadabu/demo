# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderExt(models.Model):
    _inherit = 'sale.order'

    customer_invoices_total_amount = fields.Monetary("Customer Invoices Amount", compute='_compute_total_customer_invoices_amount')

    def _compute_total_customer_invoices_amount(self):
        """
        Compute total vendor bills amount in PO
        """
        for so in self:
            so.customer_invoices_total_amount = sum(so.invoice_ids.filtered(lambda l: l.state != 'cancel').mapped('amount_total'))

    def total_customer_invoice_amount(self):
        return
