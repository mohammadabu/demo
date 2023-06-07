# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class SaleConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_with_sample = fields.Boolean('Invoice including sample', config_parameter='sync_sample_product.invoice_with_sample')