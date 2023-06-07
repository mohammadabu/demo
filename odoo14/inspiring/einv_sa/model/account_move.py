#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
# from base64 import b64encode

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning 
import logging
_logger = logging.getLogger(__name__)


def generate_tlv_hex(*args):
    """to combine all tags with conversion to hex decimal"""
    b_array = bytearray()
    for index, val in enumerate(args):
        b_array.append(index + 1)
        b_array.append(len(val))
        b_array.extend(val.encode('utf-8'))
    return b_array


def generate_tlv_base64(*args):
    tlv_hex = generate_tlv_hex(args)  # true
    return str(base64.b64encode(tlv_hex), "utf-8")


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"
    einv_amount_sale_total = fields.Monetary(string="Amount sale total", compute="_compute_total", store='True',
                                             help="")
    einv_amount_discount_total = fields.Monetary(string="Amount discount total", compute="_compute_total", store='True',
                                                 help="")
    einv_amount_tax_total = fields.Monetary(string="Amount tax total", compute="_compute_total", store='True', help="")

    # einv_qr = fields.Char(string="Amount tax total", compute="_compute_total", store='True', help="", readonly=True)

    # region odoo standard -------------------------
    einv_sa_delivery_date = fields.Date(string='Delivery Date', default=fields.Date.context_today, copy=False)
    
    
    # einv_sa_show_delivery_date = fields.Boolean(compute='_compute_show_delivery_date')
    einv_sa_show_delivery_date = fields.Boolean()
    # einv_sa_qr_code_str = fields.Char(string='Zatka QR Code', compute='_compute_qr_code_str')

    einv_sa_qr_code_str = fields.Char(string='Zatka QR Code')

    einv_sa_confirmation_datetime = fields.Datetime(string='Confirmation Date')
    # einv_sa_confirmation_datetime = fields.Datetime(string='Confirmation Date', readonly=True, copy=False)

    @api.depends('country_code', 'move_type') 
    def _compute_show_delivery_date(self):
        for move in self:
            country_code = move.country_code
            move_type = move.move_type
            if country_code != False and move_type != False:
                move.einv_sa_show_delivery_date = move.country_code == 'SA' and move.move_type in ('out_invoice', 'out_refund')
            else:
                move.einv_sa_show_delivery_date = False
    # @api.depends('amount_total', 'amount_untaxed', 'einv_sa_confirmation_datetime', 'company_id', 'company_id.vat')
    # def _compute_qr_code_str(self):
    #     """ Generate the qr code for Saudi e-invoicing. Specs are available at the following link at page 23
    #     https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
    #     https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/QRCodeCreation.pdf
    #     """


    #     def get_qr_encoding(tag, field):
    #         company_name_byte_array = field.encode('UTF-8')
    #         company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
    #         company_name_length_encoding = len(company_name_byte_array).to_bytes(length=1, byteorder='big')
    #         return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array

    #     for record in self:
    #         qr_code_str = ''

    #         amount_total = record.amount_total
    #         amount_untaxed = record.amount_untaxed
    #         einv_sa_confirmation_datetime = record.einv_sa_confirmation_datetime
    #         company_id = record.company_id
    #         # company_vat = '310018312900003'
    #         company_vat = record.company_id.vat



    #         if amount_total != False and amount_untaxed != False and einv_sa_confirmation_datetime != False and company_id != False and company_vat != False:            
    #             if record.einv_sa_confirmation_datetime and record.company_id.vat:
    #                 seller_name_enc = get_qr_encoding(1, record.company_id.display_name)
    #                 company_vat_enc = get_qr_encoding(2, record.company_id.vat)
    #                 time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'),
    #                                                             record.einv_sa_confirmation_datetime)
    #                 timestamp_enc = get_qr_encoding(3, time_sa.isoformat())
    #                 invoice_total_enc = get_qr_encoding(4, str(record.amount_total))
    #                 total_vat_enc = get_qr_encoding(5, str(record.currency_id.round(
    #                     record.amount_total - record.amount_untaxed)))

    #                 str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
    #                 qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
    #             _logger.info("qr_code_str qr_code_str")   
    #             _logger.info(qr_code_str)    
    #             record.einv_sa_qr_code_str = qr_code_str
    #         else:
    #             record.einv_sa_qr_code_str = "N/A"   



    @api.model
    def create(self,vals):
        try:   
            country_code = ''
            move_type = '' 
            if "country_code" in vals:
                country_code = vals['country_code']
            if "move_type" in vals:
                move_type = vals['move_type']

            # vals['einv_sa_show_delivery_date'] = country_code == 'SA' and move_type in ('out_invoice', 'out_refund')

            vals['einv_sa_show_delivery_date'] = True
            amount_total = ''
            amount_untaxed = ''
            einv_sa_confirmation_datetime = ''
            company_id = ''
            company_vat = '310018312900003'

            if "amount_total" in vals:
                amount_total = vals['amount_total']
            if "amount_untaxed" in vals:
                amount_untaxed = vals['amount_untaxed']
            if "einv_sa_confirmation_datetime" in vals:
                einv_sa_confirmation_datetime = vals['einv_sa_confirmation_datetime']
            if "company_id" in vals:
                company_id = vals['company_id']  

            _logger.info("einv_sa_confirmation_datetime test") 
            _logger.info(einv_sa_confirmation_datetime) 
            _logger.info(company_vat)    
            qr_code_str = ''
            if einv_sa_confirmation_datetime and company_vat:
                seller_name_enc = self.pool.get("account.move").get_qr_encoding(self,1,"test")
                _logger.info("seller_name_enc")
                _logger.info(seller_name_enc)
                # seller_name_enc = get_qr_encoding(1, record.company_id.display_name)
                company_vat_enc = self.pool.get("account.move").get_qr_encoding(self,1,"test")
                _logger.info("company_vat_enc")
                _logger.info(company_vat_enc)
                # company_vat_enc = get_qr_encoding(self ,2, company_vat)

                time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'),einv_sa_confirmation_datetime)
                
                # timestamp_enc = self.pool.get("account.move").get_qr_encoding(self,3,time_sa.isoformat())
                # # timestamp_enc = get_qr_encoding(3, time_sa.isoformat())
                # invoice_total_enc = self.pool.get("account.move").get_qr_encoding(self,4,str(amount_total))
                # # invoice_total_enc = get_qr_encoding(4, str(record.amount_total))
                # total_vat_enc = self.pool.get("account.move").get_qr_encoding(self,5,str(self.currency_id.round(self.amount_total - self.amount_untaxed)))
                # # total_vat_enc = get_qr_encoding(5, str(record.currency_id.round(record.amount_total - record.amount_untaxed)))

                # str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
                qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
            _logger.info("qr_code_str qr_code_str")   
            _logger.info(qr_code_str)    
            # record.einv_sa_qr_code_str = qr_code_str            
            vals['einv_sa_qr_code_str'] = qr_code_str




            _logger.info("createcreatecreatecreate")
            _logger.info(vals)


            #     followers_emails = self.pool.get("ir.attachment").updateUserEmail(self,employee_followers,"1")   
            #     vals['followers_emails'] = followers_emails
            #     vals['user_created'] = self.env.user.id
            #     rtn = super(CustomIrDocumentsAttachment,self).create(vals)
            #     followers_emails = self.pool.get("ir.attachment").updateUserEmail(self,employee_followers,rtn.id) 
            #     attachment = self.env['ir.attachment'].sudo().search([('id','=',rtn.id)],limit=1)
            #     attachment.write({"followers_emails":followers_emails,"only_create":True})
            #     self.pool.get("ir.attachment").updateFolderUserEmail(self,followers_emails,folder)
            #     return rtn
            # else:
            rtn = super(AccountMove,self).create(vals)
            return rtn
        except Exception as e:
            _logger.info(e)   
            rtn = super(AccountMove,self).create(vals)   
            return rtn              

    @api.model
    def get_qr_encoding(self,tag, field):
            company_name_byte_array = field.encode('UTF-8')
            company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
            company_name_length_encoding = len(company_name_byte_array).to_bytes(length=1, byteorder='big')
            return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array

    def _post(self, soft=True):
        res = super()._post(soft)
        for record in self:
            if record.country_code == 'SA' and record.move_type in ('out_invoice', 'out_refund'):
                if not record.einv_sa_show_delivery_date:
                    raise UserError(_('Delivery Date cannot be empty'))
                if record.einv_sa_delivery_date < record.invoice_date:
                    raise UserError(_('Delivery Date cannot be before Invoice Date'))
                self.write({
                    'einv_sa_confirmation_datetime': fields.Datetime.now()
                })
        return res

    # endregion

    @api.depends('invoice_line_ids', 'amount_total')
    def _compute_total(self):
        for r in self:
            r.einv_amount_sale_total = r.amount_untaxed + sum(line.einv_amount_discount for line in r.invoice_line_ids)
            r.einv_amount_discount_total = sum(line.einv_amount_discount for line in r.invoice_line_ids)
            r.einv_amount_tax_total = sum(line.einv_amount_tax for line in r.invoice_line_ids)

            # tags = seller_name, vat_no, inv_date, total, vat
            # r.einv_qr = generate_tlv_base64(r.company_id.name, r.company_id.vat, r.invoice_date, r.amount_total, )


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = "account.move.line"
    einv_amount_discount = fields.Monetary(string="Amount discount", compute="_compute_amount_discount", store='True',
                                           help="")
    einv_amount_tax = fields.Monetary(string="Amount tax", compute="_compute_amount_tax", store='True', help="")

    @api.depends('discount', 'quantity', 'price_unit')
    def _compute_amount_discount(self):
        for r in self:
            r.einv_amount_discount = r.quantity * r.price_unit * (r.discount / 100)

    @api.depends('tax_ids', 'discount', 'quantity', 'price_unit')
    def _compute_amount_tax(self):
        for r in self:
            r.einv_amount_tax = sum(r.price_subtotal * (tax.amount / 100) for tax in r.tax_ids)
