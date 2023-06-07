# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models, _


class Company(models.Model):
    _inherit = "res.company"

    qr_code_generation_config = fields.Selection([
        ('auto', 'Generate QR Code when Invoice validate/post'),
        ('manual', 'Manually Generate')], string="QR Code Generation Configuration",
        default='auto')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    qr_code_generation_config = fields.Selection(string="QR Code Generation Configuration",
        related="company_id.qr_code_generation_config", readonly=False)
