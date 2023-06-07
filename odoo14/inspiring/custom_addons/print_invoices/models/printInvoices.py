# -*- coding: utf-8 -*-


from odoo import api, fields, models, api, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class PrintInvoices(models.Model):
    _inherit = 'account.move'

