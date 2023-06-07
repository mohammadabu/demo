from odoo import models, fields, api, _
import json
import logging
_logger = logging.getLogger(__name__)

class Edit_Scrap_Order(models.Model):
      _inherit = 'stock.scrap'
      reason = fields.Char(string='Reason')

class EditStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    unit_cost = fields.Monetary('Unit Cost', readonly=True)

class Edit_Stock_Picking(models.Model):
    _inherit = 'stock.picking'
    invoice_id = fields.Many2one(
        'account.move', 'Invoice',
        copy=False, readonly=True, tracking=True, compute="compute_invoice_id")
    
    def compute_invoice_id(self):
        for record in self:
            # sale = self.env['sale.order'].sudo().search([('name', '=', record.origin)], limit=1)
            invoice = self.env['account.move'].sudo().search([('sale_order', '=', record.sale_id.id)], limit=1)
            # _logger.info('==========================')
            # _logger.info('sale_ob %s', sale)
            # _logger.info('==========================')
            # _logger.info('invoice_ob %s', invoice)
            # _logger.info('==========================')
            record.invoice_id = invoice.id

        return


    def action_created_invoice(self):
        self.ensure_one()
        sale = self.env['sale.order'].sudo().search([('name', '=', self.origin)], limit=1)
        invoice = self.env['account.move'].sudo().search([('sale_order', '=', sale.id)], limit=1)
        return {
            'name': _('Invoice created'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'target': 'current',
            'res_id': invoice.id,
            }

