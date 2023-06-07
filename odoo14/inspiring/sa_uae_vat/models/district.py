# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today  Technaureus Info Solutions(<http://technaureus.com/>).
from odoo import api, fields, models


class ResDistrict(models.Model):
    _name = 'res.district'
    _description = "District"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    state_id = fields.Many2one('res.country.state', "State")
