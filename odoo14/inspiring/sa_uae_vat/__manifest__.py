# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

{
    'name': 'Saudi/UAE VAT(Arabic VAT)',
    'version': '14.0.0.3',
    'sequence': 1,
    'category': 'Localization',
    'summary': 'SA UAE VAT configuration',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'price': 5,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """
This module is for configure of Saudi and UAE VAT
        """,
    'depends': ['account','product','base','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/district_view.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
