from odoo import fields, models, exceptions

class Edit_Positions(models.Model):
    _inherit = 'hr.job',
    internal_id = fields.Char()

    def unlink(self):
        id_val = ''
        for record in self:
            id_val = record.internal_id
            if id_val:
                raise exceptions.ValidationError('This item cannot be deleted')
                return super(Edit_Positions, self).unlink()