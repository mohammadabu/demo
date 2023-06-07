# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Location(models.Model):
    _inherit = "stock.location"

    is_sample_location = fields.Boolean('Sample Location?', default=False)