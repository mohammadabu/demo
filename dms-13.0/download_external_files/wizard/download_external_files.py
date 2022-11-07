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

        url = 'https://my.techsfactory.com/web/image/website/1/logo/TechsFactory?unique=b499f19'
        response = requests.get(url)
        json_data = response.json()
        loaded_json = json.dumps(json_data)
        # book = json_data['items'][0]
        # image_url = book["volumeInfo"]['imageLinks']['smallThumbnail'] // here contains image url such as thumbnail
        # img = base64.b64encode(requests.get(image_url).content)
        # self.photo = img


        _logger.info("download_external_files")
        _logger.info(json_data)
        

