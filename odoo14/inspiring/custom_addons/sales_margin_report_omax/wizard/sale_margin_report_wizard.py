# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models ,SUPERUSER_ID
import time
from datetime import datetime
import calendar
import io
import base64
import xlwt
from odoo.exceptions import UserError ,ValidationError

class SaleMarginPrintExcel(models.TransientModel):

    _name = 'sale.margin.print.excel'
    _description = 'Excel Report'

    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Report File Name', readonly=True)

class SaleMarginReportWizard(models.TransientModel):
    _name = 'sale.margin.report.wizard'
    _description = 'Sale Margin Report'

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    company_ids = fields.Many2many('res.company', string="Company")
    user_ids = fields.Many2many('res.users', string="Salesperson")


    def print_sale_margin_pdf(self):
        if self.end_date < self.start_date:
            raise ValidationError('End Date should be greater than or equals to Start Date.')
        self.ensure_one()
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self.env.ref('sales_margin_report_omax.action_sale_margin_report_menu').report_action(self, data=data)

    def print_sale_margin_excel(self):
        if self.end_date < self.start_date:
            raise ValidationError('End Date should be greater than or equals to Start Date.')
        
        output = io.BytesIO()
        workbook = xlwt.Workbook(output, {'in_memory': True})
        style = xlwt.XFStyle()
        style_center = xlwt.easyxf(
            'align:vertical center, horizontal center; font:bold on; pattern: pattern solid, fore_colour gray25; border: top thin, bottom thin, right thin, left thin;')
        style_center2 = xlwt.easyxf('align:vertical center, horizontal center;')
        style_right = xlwt.easyxf('align:vertical center, horizontal right;')
        
        style_right_green = xlwt.easyxf('align:vertical center, horizontal right; font:bold on; pattern: pattern solid, fore_colour green;')
        style_right_red = xlwt.easyxf('align:vertical center, horizontal right; font:bold on; pattern: pattern solid, fore_colour red;')
        
        main_title = xlwt.easyxf(
            'align:vertical center, horizontal center; font:bold on; font:height 300; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;')
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        style.font = font
        
        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write_merge(0, 1, 0, 11, 'Sales Margin Report', main_title)
        row = 3
        col = 0
        worksheet.write(row, col, 'Start Date :')
        worksheet.write(row, 1, (self.start_date).strftime("%d/%m/%Y"))
        worksheet.write(row, 5, 'End Date :')
        worksheet.write(row, 6, (self.end_date).strftime("%d/%m/%Y"))
        
        if self.company_ids:
            company_ids = self.company_ids
        else:
            company_ids = self.env["res.company"].search([])
        if self.user_ids:
            user_ids = self.user_ids
        else:
            user_ids = self.env["res.users"].search([])
        
        row += 2
        col = 0

        worksheet.write_merge(row, row + 1, col, col, 'Order Ref', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Product', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Salesperson', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Date', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Qty', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Unit Price', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Cost', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Untaxed Amount', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Discount', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Tax', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Subtotal', style_center)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Margin Amount', style_center)

        col = 0
        row += 2
        
        user_ids_lst = []
        if user_ids:
            user_ids_lst = user_ids.ids
        
        company_id_lst = []
        if company_ids:
            company_id_lst = company_ids.ids
            
        sale_orders = self.env['sale.order'].search([
            ('user_id', 'in', user_ids_lst),
            ('company_id', 'in', company_id_lst),
            ('date_order', '>=', str(self.start_date)),
            ('date_order', '<=', str(self.end_date)),
            ('state', 'in', ('done','sale'))])
        
        total_untaxed_amount = 0
        total_discount = 0
        total_tax = 0
        total_subtotal = 0
        total_margin = 0
        for order in sale_orders:
            for orderline in order.order_line:
                worksheet.write_merge(row, row, 0, 0, order.name, style_center2)
                worksheet.write_merge(row, row, 1, 1, orderline.product_id.name, style_center2)
                worksheet.write_merge(row, row, 2, 2, order.user_id.name, style_center2)
                worksheet.write_merge(row, row, 3, 3, (order.date_order).strftime("%d/%m/%Y"), style_center2)
                worksheet.write_merge(row, row, 4, 4, round(orderline.product_uom_qty,2), style_right)
                worksheet.write_merge(row, row, 5, 5, round(orderline.price_unit,2), style_right)
                worksheet.write_merge(row, row, 6, 6, round(orderline.product_id.standard_price,2), style_right)
                
                worksheet.write_merge(row, row, 7, 7, orderline.price_subtotal, style_right)
                total_untaxed_amount += orderline.price_subtotal
                
                discount = (((orderline.price_unit * orderline.product_uom_qty) * orderline.discount) / 100)
                total_discount += discount
                worksheet.write_merge(row, row, 8, 8, round(discount,2), style_right)
                
                tax = orderline.price_total - orderline.price_subtotal
                total_tax += tax
                worksheet.write_merge(row, row, 9, 9, round(tax,2), style_right)
                
                worksheet.write_merge(row, row, 10, 10, round(orderline.price_total,2), style_right)
                total_subtotal += orderline.price_total
                
                margin =((orderline.product_uom_qty * (orderline.price_unit - orderline.product_id.standard_price)) - discount)
                total_margin += margin
                
                if margin >= 0: 
                    worksheet.write_merge(row, row, 11, 11, round(margin,2), style_right_green)
                else:
                    worksheet.write_merge(row, row, 11, 11, round(margin,2), style_right_red)
                
                row += 1
                
        worksheet.write_merge(row, row, 0, 6, 'Total', style_center)
        worksheet.write_merge(row, row, 7, 7, total_untaxed_amount, style_center)
        worksheet.write_merge(row, row, 8, 8, total_discount, style_center)
        worksheet.write_merge(row, row, 9, 9, total_tax, style_center)
        worksheet.write_merge(row, row, 10, 10, total_subtotal, style_center)
        
        if total_margin >= 0:
            worksheet.write_merge(row, row, 11, 11, total_margin, style_right_green)
        else:
            worksheet.write_merge(row, row, 11, 11, total_margin, style_right_red)
                
        
        filename = 'Sales Margin Report.xlsx'
        stream = io.BytesIO()
        workbook.save(stream)
        export_id = self.env['sale.margin.print.excel'].sudo().create({'excel_file': base64.encodebytes(stream.getvalue()), 'file_name': filename})

        return {
            'view_mode': 'form', 'res_id': export_id.id, 'res_model': 'sale.margin.print.excel', 'view_type': 'form',
            'type': 'ir.actions.act_window', 'context': self._context, 'target': 'new',
        }
        
