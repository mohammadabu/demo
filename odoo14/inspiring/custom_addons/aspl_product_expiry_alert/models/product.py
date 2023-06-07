# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
import ast
import copy
from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
from itertools import groupby
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    near_expire = fields.Integer(string='Near Expire', compute='check_near_expiry')
    expired = fields.Integer(string='Expired', compute='check_expiry')

    def get_near_expiry(self):
        expiry_lot_ids = self.env['stock.production.lot'].search([('product_id', 'in', self.ids)])
        return expiry_lot_ids.filtered(lambda l: l.product_expiry_reminder)

    def get_expiry(self):
        expiry_lot_ids = self.env['stock.production.lot'].search([('product_id', 'in', self.ids)])
        return expiry_lot_ids.filtered(lambda l: l.product_expiry_alert)

    def check_near_expiry(self):
        stock_production_lot_obj = self.get_near_expiry()
        self.near_expire = len(stock_production_lot_obj)

    def check_expiry(self):
        stock_production_lot_obj = self.get_expiry()
        self.expired = len(stock_production_lot_obj)

    def nearly_expired(self):
        stock_production_lot_obj = self.get_near_expiry()
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('id', 'in', [each_lot.id for each_lot in stock_production_lot_obj])]
        return action

    def product_expired(self):
        stock_production_lot_obj = self.get_expiry()
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('id', 'in', [each_lot.id for each_lot in stock_production_lot_obj])]
        return action

    def category_expiry(self, company_id):
        quant_sql = '''
        SELECT
            pt.name as product_name,
            sq.quantity as quantity,
            pc.name as categ_name,
            spl.id as lot_id
        FROM
            stock_quant sq
            LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
            LEFT JOIN product_product pp on pp.id = sq.product_id
            LEFT JOIN product_template pt on pt.id = pp.product_tmpl_id
            LEFT JOIN product_category pc on pc.id = pt.categ_id
        WHERE
            pt.tracking != 'none' AND
            spl.expiration_date is not NULL AND
            sq.state_check = 'near_expired' AND
            sq.company_id = %s AND
            spl.expiration_date::Date >= current_date;
        ''' % (company_id)
        self._cr.execute(quant_sql)
        result = self._cr.dictfetchall()
        return result

    @api.model
    def search_product_expiry(self):
        today = datetime.today()
        today_end_date = datetime.strftime(today, "%Y-%m-%d 23:59:59")
        today_date = datetime.strftime(today, "%Y-%m-%d 00:00:00")
        company_id = self.env.user.company_id.id
        categ_nearexpiry_data = self.category_expiry(company_id)
        location_obj = self.env['stock.location']
        location_detail = location_obj.get_location_detail(company_id)
        warehouse_detail = location_obj.get_warehouse_expiry_detail(company_id)
        exp_in_day = {}
        product_expiry_days_ids = self.env['product.expiry.config'].search([('active', '=', True)])
        if product_expiry_days_ids:
            for each in product_expiry_days_ids:
                exp_in_day[int(each.no_of_days)] = 0
        exp_in_day_detail = copy.deepcopy(exp_in_day)
        for exp_day in exp_in_day:
            product_id_list = []
            exp_date = datetime.today() + timedelta(days=exp_day)
            today_exp_date = datetime.strftime(exp_date, "%Y-%m-%d 23:59:59")
            today_expire_data_id = """
                SELECT
                    sq.lot_id
                FROM
                    stock_quant sq
                    LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
                WHERE
                    spl.expiration_date >= '%s' AND
                    spl.expiration_date <= '%s' AND
                    sq.company_id = %s AND
                    spl.state_check = 'near_expired'
                GROUP BY
                    sq.lot_id;
            """ % (today_date, today_exp_date, company_id)
            self._cr.execute(today_expire_data_id)
            result = self._cr.fetchall()
            for each in result:
                for each_in in each:
                    product_id_list.append(each_in)
            product_config_color_id = self.env['product.expiry.config'].search([('no_of_days', '=',exp_day),('active', '=', True)], limit=1)
            exp_in_day_detail[exp_day] = {'product_id': product_id_list, 'color': product_config_color_id.block_color, 'text_color': product_config_color_id.text_color}
            exp_in_day[exp_day] = len(result)

        category_list = copy.deepcopy(categ_nearexpiry_data)
        category_res = []
        key = lambda x: x['categ_name']

        for k, v in groupby(sorted(category_list, key=key), key=key):
            qty = 0
            stock_lot = []
            for each in v:
                qty += float(each['quantity']) if each['quantity'] > 0 else 0
                stock_lot.append(each['lot_id'])
            category_res.append({'categ_name': k, 'qty': qty, 'id': stock_lot})
        yesterday_date = date.today() + timedelta(days=-1)
        expiry_date_start = datetime.strftime(yesterday_date, "%Y-%m-%d 00:00:00")
        expiry_date_end = datetime.strftime(yesterday_date, "%Y-%m-%d 23:59:59")
        exp_in_day['expired'] = self.env['stock.production.lot'].search_count(
            [(['state_check', '=', 'expired']), ('expiration_date', '>=', expiry_date_start),
             ('expiration_date', '<=', expiry_date_end)])
        list_near_expire = []
        quant_sql = '''
            SELECT
                sq.lot_id as lot_id
            FROM
                stock_quant sq
                LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
            WHERE
                sq.state_check = 'near_expired' AND
                sq.company_id = %s AND
                spl.expiration_date >= '%s' AND
                spl.expiration_date <= '%s'
        ''' % (company_id, today_date, today_end_date)
        self._cr.execute(quant_sql)
        quant_detail = self._cr.dictfetchall()
        for each_quant in quant_detail:
            list_near_expire.append(each_quant.get('lot_id'))
        exp_in_day['day_wise_expire'] = exp_in_day_detail
        exp_in_day['near_expired'] = len(set(list_near_expire))
        exp_in_day['near_expire_display'] = list_near_expire
        exp_in_day['category_near_expire'] = category_res
        exp_in_day['location_wise_expire'] = location_detail
        exp_in_day['warehouse_wise_expire'] = warehouse_detail
        return exp_in_day

    def graph_date(self, start, end):
        company_id = self.env.user.company_id.id
        graph_data_list = []
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        new_start_date = datetime.strftime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        new_end_date = datetime.strftime(end_date, "%Y-%m-%d 23:59:59")

        sql = '''
            SELECT
                pt.name as product_name,
                sum(sq.quantity) AS qty
            FROM
                stock_quant sq
                LEFT JOIN stock_production_lot spl on spl.id = sq.lot_id
                LEFT JOIN product_product AS pp ON pp.id = spl.product_id
                LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            WHERE
                sq.quantity > 0 AND
                sq.company_id = %s AND
                sq.state_check is NOT NULL AND
                pt.tracking != 'none' AND
                spl.expiration_date BETWEEN '%s' AND '%s'
            GROUP BY
                pt.name;
        ''' % (company_id, new_start_date, new_end_date)
        self._cr.execute(sql)
        data_res = self._cr.dictfetchall()
        return data_res

    @api.model
    def expiry_product_alert(self):
        email_notify_date = None
        notification_days = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_product_expiry_alert.email_notification_days')

        if notification_days:
            email_notify_date = date.today() + timedelta(days=int(notification_days))
            start_email_notify_date = datetime.strftime(date.today(), "%Y-%m-%d %H:%M:%S")
            end_email_notify_date = datetime.strftime(email_notify_date, "%Y-%m-%d 23:59:59")

            res_user_ids = ast.literal_eval(
                self.env['ir.config_parameter'].sudo().get_param('aspl_product_expiry_alert.res_user_ids'))

            SQL = """
                SELECT 
                    sl.name AS stock_location, 
                    pt.name AS Product,pp.id AS product_id, 
                    CAST(lot.expiration_date AS DATE),lot.name lot_number, 
                    sq.quantity AS Quantity
                FROM 
                    stock_quant AS sq
                    INNER JOIN stock_production_lot AS lot ON lot.id = sq.lot_id 
                    INNER JOIN stock_location AS sl ON sl.id = sq.location_id
                    INNER JOIN product_product AS pp ON pp.id = lot.product_id
                    INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
                WHERE 
                    sl.usage = 'internal' AND 
                    pt.tracking != 'none' AND 
                    lot.expiration_date BETWEEN '%s' AND '%s'
            """ %(start_email_notify_date,end_email_notify_date)
            self._cr.execute(SQL)
            near_expiry_data_list = self._cr.dictfetchall()
            email_list = []
            template_id = self.env.ref('aspl_product_expiry_alert.email_template_product_expiry_alert')
            res_user_ids = self.env['res.users'].browse(res_user_ids)
            email_list = [x.email for x in res_user_ids if x.email]
            email_list_1 = ', '.join(map(str, email_list))
            company_name = self.env.user.company_id.name
            if res_user_ids and template_id and near_expiry_data_list:
                # template_id.send_mail(int(near_expiry_data_list[0]['product_id']), force_send=True)
                template_id.with_context({'company': company_name,'email_list': email_list_1, 'from_dis': True,
                                          'data_list': near_expiry_data_list}).send_mail(int(near_expiry_data_list[0]['product_id']), force_send=True)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: