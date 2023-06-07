# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_stock = fields.Boolean(string="Sale Order Without Stock")