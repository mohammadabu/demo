# -*- coding: utf-8 -*-

from odoo import models, fields
import base64
import requests
import logging
_logger = logging.getLogger(__name__)

class DownloadExternalFiles(models.TransientModel):
    _name = 'custom_upload_images.wizard'

    # stages = fields.Many2many('project.project.stages')
    def download_external_files(self):
        _logger.info("download_external_files")
        url = 'https://my.techsfactory.com/web/image/website/1/logo/TechsFactory?unique=b499f19'
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code != 204:
            json_data = response.json()
            _logger.info(json_data)
        else:
            _logger.info(response)
        # loaded_json = json.dumps(json_data)
        # book = json_data['items'][0]
        # image_url = book["volumeInfo"]['imageLinks']['smallThumbnail'] // here contains image url such as thumbnail
        # img = base64.b64encode(requests.get(image_url).content)
        # self.photo = img
        

