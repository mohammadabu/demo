from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class Edit_Lot_Number(models.Model):
    _inherit = "stock.production.lot"
    _description = "Edit Lot fields"

    rack_no = fields.Char('Rack No.')
    aisle_no = fields.Char('Aisle No.')

class Edit_Lot_Name(models.Model):
    _inherit = "stock.move.line"
    _description = "Edit Lot fields"

    lot_serial_list = fields.Many2one(
        'stock.production.lot', domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]")

    @api.onchange('lot_serial_list')
    def _change_lot_name(self):
        for line in self:
            if line.lot_serial_list.name:
                self.lot_name = line.lot_serial_list.name