# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.
#      Copying is not allowed.
#
###############################################################################

# from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

    # credit_limit = fields.Float(
    #     related='partner_id.credit_limit'
    # )

    # balance = fields.Monetary(
    #     related="partner_id.balance" , string="Current Balance",)
   
    # def sale_credit_limit(self):
    #     self.ensure_one()
    #     if self.partner_id.set_credit_limit ==True:
    #         if (self.partner_id.balance + self.amount_total) > self.partner_id.credit_limit:
    #             if not self.partner_id.hold_credit_limit:
    #                 msg = "Name: %s \n\
    #                         Current balance = %s \n\
    #                         Credit Limit = %s\
    #                             " % (self.partner_id.name,self.partner_id.balance, self.partner_id.credit_limit)
    #                 raise UserError(_('Customer over credit !\n' + msg))
    #     return True

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     for order in self:
    #         order.sale_credit_limit()
    #     return res
