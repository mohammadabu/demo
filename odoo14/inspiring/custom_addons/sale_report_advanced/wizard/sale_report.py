# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import json
import io
from datetime import datetime
from xlsxwriter import workbook

from odoo.tools import date_utils
from odoo import fields, models
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SaleReportAdvance(models.TransientModel):
    _name = "sale.report.advance"

    city = fields.Char(string="City")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_number = fields.Many2many('account.move', string="Invoice Number")
    salesmen_ids = fields.Many2many('res.partner', string="Sales Men", relation="salesmen_ids")
    customer_ids = fields.Many2many('res.partner', string="Customers", relation="customer_ids")
    product_ids = fields.Many2many('product.product', string='Products')
    from_date = fields.Date(string="Start Date")
    to_date = fields.Date(string="End Date")
    type = fields.Selection([('customer', 'Customers'), ('product', 'Products'), ('salesman', 'Sale Person'), ('both', 'All')],
                            string='Report Print By', default='customer', reqired=True)
    company_ids = fields.Many2many('res.company', string='Companies')
    today_date = fields.Date(default=fields.Date.today())

    def _get_data(self):
        domain = [('state','!=','cancel'), ('invoice_ids', '!=', False)]
        line_domain = [('order_id.state','!=','cancel'), ('invoice_lines', '!=', False)]

        if self.salesmen_ids:
            domain.append(('user_id.partner_id.id','in', self.salesmen_ids.ids))
            line_domain.append(('order_id.user_id.partner_id.id','in', self.ids))
        if self.city:
            domain.append(('user_id.partner_id.city','=', self.city))
            line_domain.append(('order_id.user_id.partner_id.city','=', self.city))

        sale = self.env['sale.order'].search(domain)
        sales_order_line = self.env['sale.order.line'].search(line_domain)

        if self.from_date and self.to_date and self.company_ids:
            sales_order = list(filter(lambda
                                          x: x.date_order.date() >= self.from_date and x.date_order.date() <= self.to_date and x.company_id in self.company_ids,
                                      sale))
        elif not self.from_date and self.to_date and self.company_ids:
            sales_order = list(filter(lambda
                                          x: x.date_order.date() <= self.to_date and x.company_id in self.company_ids,
                                      sale))
        elif self.from_date and not self.to_date and self.company_ids:
            sales_order = list(filter(lambda
                                          x: x.date_order.date() >= self.from_date and x.company_id in self.company_ids,
                                      sale))
        elif self.from_date and self.to_date and not self.company_ids:
            sales_order = list(filter(lambda
                                          x: x.date_order.date() >= self.from_date and x.date_order.date() <= self.to_date,
                                      sale))
        elif not self.from_date and not self.to_date and self.company_ids:
            sales_order = list(filter(lambda
                                          x: x.company_id in self.company_ids,
                                      sale))
        elif not self.from_date and self.to_date and not self.company_ids:
            sales_order = list(filter(lambda
                                          x: x.date_order.date() <= self.to_date,
                                      sale))
        elif self.from_date and not self.to_date and not self.company_ids:
            sales_order = list(filter(lambda
                                          x: x.date_order.date() >= self.from_date,
                                      sale))
        else:
            sales_order = sale
        result = []
        customers = []
        products = []
        invoices = []
        for rec in self.customer_ids:
            a = {
                'id': rec,
                'name': rec.name
            }
            customers.append(a)
        for rec in self.product_ids:
            a = {
                'id': rec,
                'name': rec.name
            }
            products.append(a)
        for rec in self.invoice_number:
            a = {
                'id': rec,
                'name': rec.name,
                'invoice_date': rec.invoice_date
            }
            invoices.append(a)
        if self.invoice_number:
            for lines in sales_order_line:
                if lines.invoice_lines:
                    for invoice_line in lines.invoice_lines:
                        if invoice_line.move_id.id in self.invoice_number.ids and lines.order_id.partner_id.id not in self.customer_ids.ids:
                            profit = round(invoice_line.price_unit - lines.product_id.standard_price, 2)
                            total_cost = round(invoice_line.price_unit * lines.qty_invoiced, 4)
                            total_price = round(lines.product_id.standard_price * lines.qty_invoiced, 4)
                            invoice_name = invoice_line.move_id.name
                            invoice_date = invoice_line.move_id.invoice_date
                            if lines.product_id.standard_price != 0:
                                margin = round((profit * 100) / lines.product_id.standard_price, 2)
                            res = {
                                'sequence': lines.order_id.name,
                                'date': lines.order_id.date_order,
                                'product_id': lines.product_id,
                                'product': lines.product_id.name,
                                'quantity': lines.qty_invoiced,
                                'cost': lines.product_id.standard_price,
                                'price': invoice_line.price_unit,
                                'profit': profit,
                                'margin': margin,
                                'partner': lines.order_id.partner_id.name,
                                'city': lines.order_id.user_id.partner_id.city or '',
                                'partner_id': lines.order_id.partner_id,
                                'salesman': lines.order_id.user_id.partner_id.name,
                                'total_cost': total_cost,
                                'total_price': total_price,
                                'invoice':  invoice_name,
                                'invoice_date': invoice_date or '' ,
                            }
                            _logger.info('invoice_res %s', res)
                            result.append(res)
        if self.invoice_date:
            for lines in sales_order_line:
                if lines.invoice_lines:
                    for invoice_line in lines.invoice_lines:
                        if invoice_line.move_id.invoice_date == self.invoice_date and invoice_line.move_id.id not in self.invoice_number.ids and lines.order_id.partner_id.id not in self.customer_ids.ids:
                            profit = round(invoice_line.price_unit - lines.product_id.standard_price, 2)
                            total_cost = round(invoice_line.price_unit * lines.qty_invoiced, 4)
                            total_price = round(lines.product_id.standard_price * lines.qty_invoiced, 4)
                            invoice_name = invoice_line.move_id.name
                            invoice_date = invoice_line.move_id.invoice_date
                            if lines.product_id.standard_price != 0:
                                margin = round((profit * 100) / lines.product_id.standard_price, 2)
                            res = {
                                'sequence': lines.order_id.name,
                                'date': lines.order_id.date_order,
                                'product_id': lines.product_id,
                                'product': lines.product_id.name,
                                'quantity': lines.qty_invoiced,
                                'cost': lines.product_id.standard_price,
                                'price': invoice_line.price_unit,
                                'profit': profit,
                                'margin': margin,
                                'partner': lines.order_id.partner_id.name,
                                'city': lines.order_id.user_id.partner_id.city or '',
                                'partner_id': lines.order_id.partner_id,
                                'salesman': lines.order_id.user_id.partner_id.name,
                                'total_cost': total_cost,
                                'total_price': total_price,
                                'invoice':  invoice_name,
                                'invoice_date': invoice_date or '' ,
                            }
                            result.append(res)
        if self.type == 'product':
            for rec in products:
                for lines in sales_order_line:
                    if lines.product_id == rec['id'] and lines.invoice_lines:
                        for invoice_line in lines.invoice_lines:
                            profit = round(invoice_line.price_unit - lines.product_id.standard_price, 2)
                            total_cost = round(invoice_line.price_unit * lines.qty_invoiced, 4)
                            total_price = round(lines.product_id.standard_price * lines.qty_invoiced, 4)
                            invoice_name = invoice_line.move_id.name
                            invoice_date = invoice_line.move_id.invoice_date
                            if lines.product_id.standard_price != 0:
                                margin = round((profit * 100) / lines.product_id.standard_price, 2)
                            res = {
                                'sequence': lines.order_id.name,
                                'date': lines.order_id.date_order,
                                'product_id': lines.product_id,
                                'quantity': lines.qty_invoiced,
                                'cost': lines.product_id.standard_price,
                                'price': invoice_line.price_unit,
                                'profit': profit,
                                'margin': margin,
                                'partner': lines.order_id.partner_id.name,
                                'city': lines.order_id.user_id.partner_id.city or '',
                                'salesman': lines.order_id.user_id.partner_id.name,
                                'total_cost': total_cost,
                                'total_price': total_price,
                                'invoice':  invoice_name,
                                'invoice_date': invoice_date or '' ,
                            }
                            result.append(res)
        if self.type == 'customer':
            for rec in customers:
                for so in sales_order:
                    if so.partner_id == rec['id']:
                        for lines in so.order_line:
                            if lines.invoice_lines:
                                for invoice_line in lines.invoice_lines:
                                    profit = round(invoice_line.price_unit - lines.product_id.standard_price, 2)
                                    total_cost = round(invoice_line.price_unit * lines.qty_invoiced, 4)
                                    total_price = round(lines.product_id.standard_price * lines.qty_invoiced, 4)
                                    if lines.product_id.standard_price != 0:
                                        margin = round((profit * 100) / lines.product_id.standard_price, 2)
                                    invoice_name = lines.invoice_lines[-1].move_id.name
                                    invoice_date = lines.invoice_lines[-1].move_id.invoice_date
                                    res = {
                                        'sequence': so.name,
                                        'date': so.date_order,
                                        'product': lines.product_id.name,
                                        'quantity': lines.qty_invoiced,
                                        'cost': lines.product_id.standard_price,
                                        'price': invoice_line.price_unit,
                                        'profit': profit,
                                        'margin': margin,
                                        'partner_id': so.partner_id,
                                        'city': lines.order_id.user_id.partner_id.city or '',
                                        'salesman': lines.order_id.user_id.partner_id.name,
                                        'total_cost': total_cost,
                                        'total_price': total_price,
                                        'invoice':  invoice_name,
                                        'invoice_date': invoice_date or '' ,
                                    }
                                    result.append(res)
        if self.type == 'both':
            for rec in customers:
                for p in products:
                    for so in sales_order:
                        if so.partner_id == rec['id']:
                            for lines in so.order_line:
                                if lines.product_id == p['id'] and lines.invoice_lines:
                                    for invoice_line in lines.invoice_lines:
                                        profit = round(invoice_line.price_unit - lines.product_id.standard_price, 2)
                                        total_cost = round(invoice_line.price_unit * lines.qty_invoiced, 4)
                                        total_price = round(lines.product_id.standard_price * lines.qty_invoiced, 4)
                                        invoice_name = lines.invoice_lines[-1].move_id.name
                                        invoice_date = lines.invoice_lines[-1].move_id.invoice_date
                                        if lines.product_id.standard_price != 0:
                                            margin = round((profit * 100) / lines.product_id.standard_price, 2)
                                        res = {
                                            'sequence': so.name,
                                            'date': so.date_order,
                                            'product': lines.product_id.name,
                                            'quantity': lines.qty_invoiced,
                                            'cost': lines.product_id.standard_price,
                                            'price': invoice_line.price_unit,
                                            'profit': profit,
                                            'margin': margin,
                                            'partner': so.partner_id.name,
                                            'city': so.user_id.partner_id.city or '',
                                            'salesman': so.user_id.partner_id.name,
                                            'total_cost': total_cost,
                                            'total_price': total_price,
                                            'invoice':  invoice_name,
                                            'invoice_date': invoice_date or '',
                                        }
                                        result.append(res)
        if self.from_date and self.to_date and not self.customer_ids and not self.product_ids and not self.invoice_number and not self.invoice_date:
            for so in sales_order:
                for lines in so.order_line:
                    if lines.invoice_lines:
                        for invoice_line in lines.invoice_lines:
                            profit = round(invoice_line.price_unit - lines.product_id.standard_price, 2)
                            total_cost = round(invoice_line.price_unit * lines.qty_invoiced, 4)
                            total_price = round(lines.product_id.standard_price * lines.qty_invoiced, 4)
                            margin = 0
                            invoice_name = lines.invoice_lines[-1].move_id.name
                            invoice_date = lines.invoice_lines[-1].move_id.invoice_date
                            if lines.product_id.standard_price != 0:
                                margin = round((profit * 100) / lines.product_id.standard_price, 2)
                            res = {
                                'sequence': so.name,
                                'date': so.date_order,
                                'product': lines.product_id.name,
                                'quantity': lines.qty_invoiced,
                                'cost': lines.product_id.standard_price,
                                'price': invoice_line.price_unit,
                                'profit': profit,
                                'margin': margin,
                                'partner': so.partner_id.name,
                                'city': so.user_id.partner_id.city or '',
                                'salesman': so.user_id.partner_id.name,
                                'total_cost': total_cost,
                                'total_price': total_price,
                                'invoice':  invoice_name,
                                'invoice_date': invoice_date or '' ,
                            }
                            result.append(res)

        datas = {
            'ids': self,
            'model': 'sale.report.advance',
            'form': result,
            'partner_id': customers,
            'product_id': products,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'type': self.type,
            'no_value': False,

        }
        if self.from_date and self.to_date and not self.customer_ids and not self.product_ids:
            datas['no_value']=True
        return datas

    def get_report(self):
        datas = self._get_data()
        return self.env.ref('sale_report_advanced.action_sale_report').report_action([], data=datas)

    def get_excel_report(self):
        datas = self._get_data()
        return {
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'data': {'model': 'sale.report.advance',
                     'output_format': 'xlsx',
                     'options': json.dumps(datas, default=date_utils.json_default),
                     'report_name': 'Sale Product Profit',
                     },
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet()
        record = []
        cell_format = workbook.add_format({})
        head = workbook.add_format({'align': 'center', 'bold': True})
        txt = workbook.add_format({'align': 'center'})
        format1 = workbook.add_format(
            {'font_size': 10, 'align': 'center','bg_color':'#d3d3d3','border': 1})
        format2 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'bold': True,
             'bg_color': '#6BA6FE', 'border': 1})
        format4 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'bold': True,'border': 1})
        format3 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'bold': True, 'bg_color': '#d3d3d3', 'border': 1})

        sheet.merge_range('A2:B3', 'Sales Profit Report', head)
        if data['start_date'] and data['end_date']:
            sheet.write('A6', 'From:', cell_format)
            sheet.merge_range('B6:C6', data['start_date'], txt)
            sheet.write('D6', 'To:', cell_format)
            sheet.merge_range('E6:F6', data['end_date'], txt)
        if data['type'] == 'product':
            record = data['product_id']
        if data['type'] == 'customer':
            record = data['partner_id']
        h_row = 7
        h_col = 3
        count = 0
        row = 5
        col = 0
        row_number = 6
        t_row = 8
        if data['type'] == 'product' or data['type'] == 'customer':
            for rec in record:
                col = 0
                sheet.merge_range(h_row, h_col-3,h_row,h_col+4,rec['name'], format3)
                row = row + count + 3
                sheet.write(row, col, 'City', format2)
                col += 1
                sheet.write(row, col, 'Invoice Number', format2)
                col += 1
                sheet.write(row, col, 'Invoice Date', format2)
                col += 1
                sheet.write(row, col, 'Order', format2)
                col += 1
                sheet.write(row, col, 'Date', format2)
                col += 1
                if data['type'] == 'product':
                    sheet.write(row, col, 'Customer', format2)
                    col += 1
                elif data['type'] == 'customer':
                    sheet.write(row, col, 'Product', format2)
                    col += 1
                sheet.write(row, col, 'Quantity', format2)
                col += 1
                sheet.write(row, col, 'Cost', format2)
                col += 1
                sheet.write(row, col, 'Price', format2)
                col += 1
                sheet.write(row, col, 'Total Sales', format2)
                col += 1
                sheet.write(row, col, 'Total Cost', format2)
                col += 1
                sheet.write(row, col, 'Profit', format2)
                col += 1
                sheet.write(row, col, 'Margin(%)', format2)
                col += 1
                sheet.write(row, col, 'SalesMan Name', format2)
                col += 1
                t_row += 1
                col = 6
                count = 0
                row_number = row_number + count + 3
                t_qty = 0
                t_cost = 0
                t_price = 0
                t_profit = 0
                t_total_cost = 0
                t_total_price = 0
                t_margin = 0
                t_col = 5
                for val in data['form']:
                    if data['type'] == 'customer':
                        if val['partner_id'] == rec['id']:
                            count += 1
                            column_number = 0
                            sheet.write(row_number, column_number, val['city'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['invoice'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['invoice_date'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['sequence'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['date'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['product'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['quantity'], format1)
                            t_qty += val['quantity']
                            column_number += 1
                            sheet.write(row_number, column_number, val['cost'], format1)
                            t_cost += val['cost']
                            column_number += 1
                            sheet.write(row_number, column_number, val['price'], format1)
                            t_price += val['price']
                            column_number += 1
                            sheet.write(row_number, column_number, val['total_cost'], format1)
                            t_total_cost += val['total_cost']
                            column_number += 1
                            sheet.write(row_number, column_number, val['total_price'], format1)
                            t_total_price += val['total_price']
                            column_number += 1
                            sheet.write(row_number, column_number, val['profit'], format1)
                            t_profit += val['profit']
                            column_number += 1
                            sheet.write(row_number, column_number, val['margin'], format1)
                            t_margin += val['margin']
                            column_number += 1
                            sheet.write(row_number, column_number, val['salesman'], format1)
                            column_number += 1
                            row_number += 1
                            t_row += 1
                    if data['type'] == 'product':
                        if val['product_id'] == rec['id']:
                            count += 1
                            column_number = 0
                            sheet.write(row_number, column_number, val['city'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['invoice'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['invoice_date'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['sequence'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['date'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['partner'], format1)
                            column_number += 1
                            sheet.write(row_number, column_number, val['quantity'], format1)
                            t_qty += val['quantity']
                            column_number += 1
                            sheet.write(row_number, column_number, val['cost'], format1)
                            t_cost += val['cost']
                            column_number += 1
                            sheet.write(row_number, column_number, val['price'], format1)
                            t_price += val['price']
                            column_number += 1
                            sheet.write(row_number, column_number, val['total_cost'], format1)
                            t_total_cost += val['total_cost']
                            column_number += 1
                            sheet.write(row_number, column_number, val['total_price'], format1)
                            t_total_price += val['total_price']
                            column_number += 1
                            sheet.write(row_number, column_number, val['profit'], format1)
                            t_profit += val['profit']
                            column_number += 1
                            sheet.write(row_number, column_number, val['margin'], format1)
                            t_margin += val['margin']
                            column_number += 1
                            sheet.write(row_number, column_number, val['salesman'], format1)
                            column_number += 1
                            row_number += 1
                            t_row += 1
                sheet.write(t_row, t_col, 'Total', format4)
                t_col += 1
                sheet.write(t_row, t_col, t_qty, format4)
                t_col += 1
                sheet.write(t_row, t_col, t_cost, format4)
                t_col += 1
                sheet.write(t_row, t_col, t_price, format4)
                t_col += 1
                sheet.write(t_row, t_col, t_total_cost, format4)
                t_col += 1
                sheet.write(t_row, t_col, t_total_price, format4)
                t_col += 1
                sheet.write(t_row, t_col, t_profit, format4)
                t_col += 1
                sheet.write(t_row, t_col, t_margin, format4)
                t_col += 1
                h_row = h_row + count + 3
        if data['type'] == 'both' or data['no_value'] == True:
            row += 3
            row_number += 2
            t_qty = 0
            t_cost = 0
            t_price = 0
            t_profit = 0
            t_total_cost = 0
            t_total_price = 0
            t_margin = 0
            t_col = 6
            sheet.write(row, col, 'City', format2)
            col += 1
            sheet.write(row, col, 'Invoice Number', format2)
            col += 1
            sheet.write(row, col, 'Invoice Date', format2)
            col += 1
            sheet.write(row, col, 'Order', format2)
            col += 1
            sheet.write(row, col, 'Date', format2)
            col += 1
            sheet.write(row, col, 'Customer', format2)
            col += 1
            sheet.write(row, col, 'Product', format2)
            col += 1
            sheet.write(row, col, 'Quantity', format2)
            col += 1
            sheet.write(row, col, 'Cost', format2)
            col += 1
            sheet.write(row, col, 'Price', format2)
            col += 1
            sheet.write(row, col, 'Total Sales', format2)
            col += 1
            sheet.write(row, col, 'Total Cost', format2)
            col += 1
            sheet.write(row, col, 'Profit', format2)
            col += 1
            sheet.write(row, col, 'Margin', format2)
            col += 1
            sheet.write(row, col, 'SalesMan Name', format2)
            col += 1
            row_number+=1
            for val in data['form']:
                column_number = 0
                sheet.write(row_number, column_number, val['city'], format1)
                column_number += 1
                sheet.write(row_number, column_number, val['invoice'], format1)
                column_number += 1
                sheet.write(row_number, column_number, val['invoice_date'], format1)
                column_number += 1
                sheet.write(row_number, column_number, val['sequence'], format1)
                column_number += 1
                sheet.write(row_number, column_number, val['date'], format1)
                column_number += 1
                sheet.write(row_number, column_number, val['partner'], format1)
                column_number += 1
                sheet.write(row_number, column_number, val['product'], format1)
                column_number += 1
                sheet.write(row_number, column_number, val['quantity'], format1)
                t_qty += val['quantity']
                column_number += 1
                sheet.write(row_number, column_number, val['cost'], format1)
                t_cost += val['cost']
                column_number += 1
                sheet.write(row_number, column_number, val['price'], format1)
                t_price += val['price']
                column_number += 1
                sheet.write(row_number, column_number, val['total_cost'], format1)
                t_total_cost += val['total_cost']
                column_number += 1
                sheet.write(row_number, column_number, val['total_price'], format1)
                t_total_price += val['total_price']
                column_number += 1
                sheet.write(row_number, column_number, val['profit'], format1)
                t_profit += val['profit']
                column_number += 1
                sheet.write(row_number, column_number, val['margin'], format1)
                t_margin += val['margin']
                column_number += 1
                sheet.write(row_number, column_number, val['salesman'], format1)
                column_number += 1
                row_number += 1
            sheet.write(row_number, t_col, 'Total', format4)
            t_col += 1
            sheet.write(row_number, t_col, t_qty, format4)
            t_col += 1
            sheet.write(row_number, t_col, t_cost, format4)
            t_col += 1
            sheet.write(row_number, t_col, t_price, format4)
            t_col += 1
            sheet.write(row_number, t_col, t_total_cost, format4)
            t_col += 1
            sheet.write(row_number, t_col, t_total_price, format4)
            t_col += 1
            sheet.write(row_number, t_col, t_profit, format4)
            t_col += 1
            sheet.write(row_number, t_col, t_margin, format4)
            t_col += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()