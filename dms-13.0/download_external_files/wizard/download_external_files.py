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
        url = 'https://images.ctfassets.net/yadj1kx9rmg0/wtrHxeu3zEoEce2MokCSi/cf6f68efdcf625fdc060607df0f3baef/quwowooybuqbl6ntboz3.jpg?fm=jpg'
        response = requests.get(url)
        response.raise_for_status()
        _logger.info(response)
        try:
            if response.status_code != 204:
                # json_data = response.json()
                _logger.info("json_data")
                _logger.info(response.content)
            else:
                _logger.info("response")
                _logger.info(response)
        except Exception as e:
            _logger.info(str(e))      
        # loaded_json = json.dumps(json_data)
        # book = json_data['items'][0]
        # image_url = book["volumeInfo"]['imageLinks']['smallThumbnail'] // here contains image url such as thumbnail
        # img = base64.b64encode(requests.get(image_url).content)
        # self.photo = img
        

