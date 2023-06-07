from odoo import models, fields, api


class ReportDownloadWizard(models.TransientModel):
    _name = 'report.download.wizard'

    name = fields.Char(string="Name", readonly=True)
    data = fields.Binary(string="Download", readonly=True)
