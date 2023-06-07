# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.
import base64
import binascii
import codecs
from datetime import datetime
from io import BytesIO

from odoo import api, fields, models, _
import qrcode

from odoo.exceptions import UserError
from odoo.tools.safe_eval import pytz


class AccountMove(models.Model):
    _inherit = 'account.move'

    date_issue = fields.Date(string="Date of Issue")
    date_supply = fields.Date(string="Date of Supply")
    qr_code = fields.Binary(string='QR code', copy=False)
    generate_method = fields.Selection(related="company_id.qr_code_generation_config",
                                       )

    def _get_qr_code_method(self):
        for rec in self:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            rec.generate_method = ICPSudo.get_param('saudi_vat_invoice.qr_code_generation_config')

    def get_amount_vat_exclude(self):
        amt = 0.0
        for line in self.invoice_line_ids:
            amt = amt + line.quantity * line.price_unit
        return amt

    def get_discount(self):
        dis = 0.0
        for line in self.invoice_line_ids:
            dis = dis + ((line.price_unit * line.discount) / 100)
        return dis

    def _string_to_hex(self, value):
        if value:
            string = str(value)
            string_bytes = string.encode("UTF-8")
            encoded_hex_value = binascii.hexlify(string_bytes)
            hex_value = encoded_hex_value.decode("UTF-8")
            # print("This : "+value +"is Hex: "+ hex_value)
            return hex_value

    def _get_hex(self, tag, length, value):
        if tag and length and value:
            # str(hex(length))
            hex_string = self._string_to_hex(value)
            length = int(len(hex_string) / 2)
            # print("LEN", length, " ", "LEN Hex", hex(length))
            conversion_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
            hexadecimal = ''
            while (length > 0):
                remainder = length % 16
                hexadecimal = conversion_table[remainder] + hexadecimal
                length = length // 16
            # print(hexadecimal)
            if len(hexadecimal) == 1:
                hexadecimal = "0" + hexadecimal
            return tag + hexadecimal + hex_string

    def get_qr_code_data(self):

        if self.move_type!='entry':

            if self.move_type in ('out_invoice', 'out_refund'):
                if self.partner_id.company_type == 'company':
                    if not self.company_id.vat:
                        raise UserError('VAT Number is Missing!!! Please Configure VAT Number..')
                sellername = str(self.company_id.name)
                seller_vat_no = self.company_id.vat or ''
                if self.partner_id.company_type == 'company':
                    customer_name = self.partner_id.name
                    customer_vat = self.partner_id.vat
            else:
                if self.partner_id.company_type == 'company':
                    if not self.partner_id.vat:
                        raise UserError('VAT Number is Missing!!! Please Configure VAT..')
                sellername = str(self.partner_id.name)
                seller_vat_no = str(self.partner_id.vat)

            seller_hex = self._get_hex("01", "0c", sellername)
            vat_hex = self._get_hex("02", "0f", seller_vat_no)
            self_user = self.env.user
            if self.env.user.tz:
                date_time = datetime.now()

                normal_invoice_date = date_time.strftime("%Y-%m-%dT%H:%M:%S")
                normal_invoice_date1 = datetime.strptime(normal_invoice_date, "%Y-%m-%dT%H:%M:%S")
                inv_date_time = normal_invoice_date1.astimezone(pytz.timezone(self.env.user.tz)).isoformat()
                inv_date_time = inv_date_time.split('+')[0] + 'Z'
            else:
                raise UserError('Time Zone is Missing!!! Please Set Timezone for the User..')
            date_hex = self._get_hex("03", "14", inv_date_time)
            total_with_vat_hex = self._get_hex("04", "0a", str(round(self.amount_total, 2)))
            total_vat_hex = self._get_hex("05", "09", str(round(self.amount_tax, 2)))

            qr_hex = seller_hex + vat_hex + date_hex + total_with_vat_hex + total_vat_hex
            encoded_base64_bytes = base64.b64encode(bytes.fromhex(qr_hex)).decode()
            return encoded_base64_bytes

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.generate_method == 'auto':
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.get_qr_code_data())
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            self.qr_code = qr_image

        return res

    def net_amount_to_words(self, amount):
        return self.currency_id.amount_to_text(amount)

    def generate_qr_code(self):
        if self.move_type!='entry':
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.get_qr_code_data())
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            self.qr_code = qr_image
