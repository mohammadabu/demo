from odoo import models, api


class GroupByCustomerPaymentPdf(models.AbstractModel):
    _name = 'report.product_damage_report.product_dmg_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'data': data['stock'],
            'doc_model': 'product.damage.report',
        }