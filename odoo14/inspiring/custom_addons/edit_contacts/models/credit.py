# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

class Credit(models.Model):
    _name = 'contacts.credit'
    title = fields.Char(string='Title')
    title_ar = fields.Char(string='Arabic Title')
    credit_amount = fields.Char(string='Credit Amount')