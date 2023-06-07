from odoo import models, fields, api
class User_Default_Value(models.Model):
    _inherit = 'res.users'
    # @api.model
    # def create(self, vals):
    #     if not vals.get('sel_groups_50_51'):
    #         vals['sel_groups_50_51'] = 50
    #     rtn = super(User_Default_Value, self).create(vals)
    #     return rtn
    #
    # @api.model
    # def write(self, vals):
    #     if not vals.get('sel_groups_50_51'):
    #         vals['sel_groups_50_51'] = 50
    #     rtn = super(User_Default_Value, self).write(vals)
    #     return rtn