# -*- coding: utf-8 -*-
#################################################################################
# Author : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Product Expiry Report (Community)',
    'version': '1.0',
    'summary': 'Product Expiry Report',
    'description': """
        To print a report products which are expiring
    """,
    'category': 'General',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 20.00,
    'currency': 'EUR',
    'depends': ['stock', 'base', 'product'],
    'images': ['static/description/product_expiry_report_filter_data_wizard.png'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/grp_category_product_expiry_report_template.xml',
        'wizard/product_expiry_report_wizard_view.xml',
        'views/product_expiry_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
