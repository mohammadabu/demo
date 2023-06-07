#############
Documentation
#############

Please take attention that this module is a technical Module.
This module contains a mixin model, that you can inherit on every Model.


example how you could activate recurring documents for Invoices
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


..  code-block:: python

	from odoo import models,fields,api

	class AccountInvoice(models.Model):
	    _name = 'account.invoice'
	    _inherit = ['recurring.document','account.invoice']