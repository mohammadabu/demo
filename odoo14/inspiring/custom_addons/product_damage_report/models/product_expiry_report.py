import xlwt
import base64
from io import BytesIO
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import xlwt
from odoo.exceptions import Warning, UserError
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ProductDamageReport(models.Model):
    _name = "product.damage.report"

    damage_date= fields.Date(string="Product Damage After", required=True)
    num_expiry_days = fields.Integer(string="Product Expire In Next", required=True)
    location_ids = fields.Many2many('stock.location', string="Location",
                                    domain=[('usage', '=', 'internal')])
    category_ids = fields.Many2many('product.category', string="Category")
    group_by = fields.Selection([('location', 'Location'), ('category', 'Category')], string="Group By",
                                default="location")

    def print_pdf_report(self):
        return self.print_product_damage_report('pdf')

    def print_xls_report(self):
        return self.print_product_damage_report('xls')

    def print_product_damage_report(self, report_type):
        if self.num_expiry_days <= 0:
            raise UserError('Number Of damage Days should be greater then 0')
        location_ids = self.location_ids.ids or self.env['stock.location'].search([('usage', '=', 'internal')]).ids
        category_ids = self.category_ids.ids or self.env['product.category'].search([]).ids

        SQL1 = '''SELECT sq.location_id,sl.usage,spl.product_id,spl.id,spl.expiration_date,spl.name,pc.name as product_category,
                                pp.default_code,pt.name as product_name 
                        FROM stock_production_lot spl
                                LEFT JOIN stock_quant sq on sq.lot_id = spl.id
                                LEFT JOIN stock_location sl on sq.location_id = sl.id
                                LEFT JOIN product_product pp on spl.product_id = pp.id
                                LEFT JOIN product_template pt on pp.product_tmpl_id  = pt.id
                                LEFT JOIN product_category pc on pt.categ_id = pc.id
                        WHERE spl.expiration_date AT TIME ZONE 'GMT' <= '%s' AND
                                    spl.expiration_date AT TIME ZONE 'GMT' >= '%s' AND
                                    pc.id IN %s order by pp.default_code''' % (
            (date.today() + timedelta(days=self.num_expiry_days)),
            date.today(),
            "(%s)" % ','.join(map(str, category_ids)))
        self.env.cr.execute(SQL1)
        res1 = self.env.cr.dictfetchall()

        temp_res = []
        for each in res1:
            if each.get('usage') in ['internal', None]:
                temp_res.append(each)
        SQL = '''SELECT sq.location_id,sl.usage,spl.product_id,spl.id,spl.expiration_date,spl.name,pc.name as product_category,
                                        pp.default_code,pt.name as product_name FROM stock_quant sq
                                        LEFT JOIN stock_location sl on sq.location_id = sl.id
                                        LEFT JOIN stock_production_lot spl on sq.lot_id = spl.id
                                        LEFT JOIN product_product pp on spl.product_id = pp.id
                                        LEFT JOIN product_template pt on pp.product_tmpl_id  = pt.id
                                        LEFT JOIN product_category pc on pt.categ_id = pc.id
                                        WHERE spl.expiration_date AT TIME ZONE 'GMT' <= '%s' AND
                                        spl.expiration_date AT TIME ZONE 'GMT' >= '%s' AND
                                        pc.id IN %s AND
                                        sq.location_id IN %s order by pp.default_code''' % (
            (date.today() + timedelta(days=self.num_expiry_days)),
            date.today(),
            "(%s)" % ','.join(map(str, category_ids)),
            "(%s)" % ','.join(map(str, location_ids)))
        self.env.cr.execute(SQL)
        res_exp = self.env.cr.dictfetchall()
        res_dmg = self.env['stock.scrap'].search([('date_done', '>=', self.damage_date)])

        res = res_exp + list(res_dmg)
        _logger.info('all_res %s', res)

        if len(res) == 0:
            raise UserError(_('No such record found for product damage.'))
        else:
            vals = {}
            for each in res:
                if hasattr(each, 'name'):
                    if each.location_id == None:
                        location_name = "--"
                    else:
                        location_name = each.location_id.display_name
                    if location_name not in vals:
                        vals[location_name] = [{'name': each.name,
                             'product_id': each.product_id.display_name,
                             'product_category': each.product_id.categ_id.name,
                             'default_code': each.product_id.default_code or '--------',
                             'expiration_date': each.date_done.strftime('%Y-%m-%d') or '--------',
                             'remaining_days': relativedelta(each.product_id.expiration_date, date.today()).days,
                             'available_qty': each.scrap_qty,
                             'reason': each.reason,
                             'status': 'DAMAGE'}
                        ]
                    else:
                        vals[location_name].append({'name': each.name,
                             'product_id': each.product_id.display_name,
                             'product_category': each.product_id.categ_id.name,
                             'default_code': each.product_id.default_code or '--------',
                             'expiration_date': each.date_done.strftime('%Y-%m-%d') or '--------',
                             'remaining_days': relativedelta(each.product_id.expiration_date, date.today()).days,
                             'available_qty': each.scrap_qty,
                             'reason': each.reason,
                             'status': 'DAMAGE'})
                else:
                    if each.get('location_id') == None:
                        location_name = "--"
                    else:
                        location_name = self.env['stock.location'].browse(
                                each.get('location_id')).display_name
                    if location_name not in vals:
                        vals[location_name] = [{'name': each.get('name'),
                            'product_id': each.get('product_name'),
                            'product_category': each.get('product_category'),
                            'default_code': each.get('default_code') or '--------',
                            'expiration_date': each.get('expiration_date').strftime('%Y-%m-%d'),
                            'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
                            'available_qty': float("{:.2f}".format(self.env['stock.production.lot'].browse(
                                each.get('id')).product_qty)) if each.get('id') else False, 
                            'reason': location_name,
                            'status': 'EXPIRY'}]
                    else:
                        vals[location_name].append({'name': each.get('name'),
                            'product_id': each.get('product_name'),
                            'product_category': each.get('product_category'),
                            'default_code': each.get('default_code') or '--------',
                            'expiration_date': each.get('expiration_date').strftime('%Y-%m-%d'),
                            'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
                            'available_qty': float("{:.2f}".format(self.env['stock.production.lot'].browse(
                                each.get('id')).product_qty)) if each.get('id') else False, 
                            'reason': location_name,
                            'status': 'EXPIRY'})

        _logger.info('all_vals %s', vals)
        vals.update({'group_by': self.group_by, 'num_days': self.num_expiry_days, 'damage_date': self.damage_date, 'today_date': date.today()})
        vals_new = {}
        vals_new.update({'stock': vals})
        if report_type == 'pdf':
            return self.env.ref('product_damage_report.product_damage_report').report_action(self,
                                                                                                  data=vals_new)
        elif report_type == 'xls':
            return self.print_xls_product_report(vals)

    def print_xls_product_report(self, vals):
        stylePC = xlwt.XFStyle()
        bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gold;")
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        stylePC.alignment = alignment
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        font = xlwt.Font()
        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.THIN
        font.bold = True
        font.height = 500
        stylePC.font = font
        stylePC.alignment = alignment
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['gold']
        stylePC.pattern = pattern
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Stock damage Report')
        for column in range(0, 7):
            worksheet.col(column).width = 5600
            column += 1
        worksheet.write_merge(1, 2, 0, 6, 'Product Damage / Expire Report', style=stylePC)
        worksheet.write(4, 0, "Product Expire In Next", bold)
        worksheet.write(4, 1, str(vals.get('num_days')) + ' Days')
        worksheet.write(4, 4, "Date", bold)
        worksheet.write(4, 5, str(vals.get('today_date')))

        worksheet.write(6, 4, "Product Damage After", bold)
        worksheet.write(6, 5, str(vals.get('damage_date')))
        row= 6
        for key, value in vals.items():
            if vals.get('group_by') and key not in ['group_by', 'num_days', 'today_date', 'damage_date']:
                worksheet.write(row, 0, "Location", bold)
                worksheet.write(row, 1, key)
                row+= 2
                if value not in [vals.get('num_day'), vals.get('today_date')]:
                    worksheet.write(row, 0, "Lot/Serial number", bold)
                    worksheet.write(row, 1, "Product", bold)
                    worksheet.write(row, 2, "Location", bold)
                    worksheet.write(row, 3, "Internal Ref", bold)
                    worksheet.write(row, 4, "Damage / Expiry Date", bold)
                    worksheet.write(row, 5, "Remaining Days", bold)
                    worksheet.write(row, 6, "Available Quantity", bold)
                    worksheet.write(row, 7, "Reason", bold)
                    worksheet.write(row, 8, "Status", bold)
                    row+= 1
                    for each in value:
                        count = 0
                        for key, val in each.items():
                            worksheet.write(row, count, val)
                            count += 1
                        row+= 1
                    row+= 1
        file_data = BytesIO()
        workbook.save(file_data)
        report_id = self.env['report.download.wizard'].create({
            'data': base64.encodestring(file_data.getvalue()),
            'name': 'Product damage Report.xlsx'
        })
        return {
            'name': 'Download Excel Report',
            'view_mode': 'form',
            'res_model': 'report.download.wizard',
            'target': 'new',
            'res_id': report_id.id,
            'type': 'ir.actions.act_window'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
