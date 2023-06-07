# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrderExt(models.Model):
    _inherit = 'purchase.order'

    vendor_bills_total_amount = fields.Monetary("Vendor bills Amount", compute='_compute_total_vendor_bills_amount')

    def _compute_total_vendor_bills_amount(self):
        """
        Compute total vendor bills amount in PO
        """
        for po in self:
            po.vendor_bills_total_amount = sum(po.invoice_ids.filtered(lambda l: l.state != 'cancel').mapped('amount_total'))

    def total_vendor_bills_amount(self):
        return
