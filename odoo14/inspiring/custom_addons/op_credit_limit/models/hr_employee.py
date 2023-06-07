# -*- coding: utf-8 -*-
from datetime import datetime, date
from dateutil import relativedelta
from odoo import api, fields, models,  SUPERUSER_ID, _, tools, exceptions
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_no = fields.Char(string='Employee No',)