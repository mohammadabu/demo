# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_stock = fields.Boolean(string="Sale Order Without Stock",related="company_id.is_stock" ,readonly=False)