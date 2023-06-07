# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrderIn(models.Model):
    _inherit = "sale.order"


    def action_confirm(self):
        res = super(SaleOrderIn, self).action_confirm()
        if self.company_id.is_stock:
            msg = "You Cant't Confirm this order because of following reasons."
            msg_added = False
            for rec in self.order_line:
                if rec.product_uom_qty > rec.product_id.qty_available:
                    msg += "\n\nYou only have this quantity %s from the product %s available in %s warehouse."%(str(rec.product_id.qty_available),str(rec.product_id.display_name),str(self.warehouse_id.display_name))
                    msg_added = True
            if msg and msg_added:
                raise UserError(_(msg))             
        return res