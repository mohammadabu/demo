# -*- coding: utf-8 -*-

from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class DownloadExternalFiles(models.TransientModel):
    _name = 'custom_upload_images.wizard'

    # stages = fields.Many2many('project.project.stages')
    def download_external_files(self):
        _logger.info("download_external_files")
        

