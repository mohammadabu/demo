# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

class CustomResUserPassword(models.TransientModel):

    _inherit = 'change.password.user'


# class CustomResPassword(models.Model):

#     _inherit = 'change.password.wizard'
