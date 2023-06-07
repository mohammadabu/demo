# -*- coding: utf-8 -*-

{
    'name': 'Out of Stock Sales Orders Restriction',
    "author": "Edge Technologies",
    'version': '14.0.1.0',
    'live_test_url': "https://youtu.be/JqpsglY6Xrg",
    "images":['static/description/main_screenshot.png'], 
    'summary': 'Out of Stock product restriction on Sale Order Restrict out of Stock product restriction on sales out of stock product restriction on sales order out of stock restriction sales unavailable products restriction sales product restriction on sales order',
    'description': 'This module will Sale Orders Restrict out-of Stock',
    'license': "OPL-1",
    'depends': ['sale_management','stock'],
    'data': [
        'views/res_company.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 10,
    'currency': "EUR",
    'category': 'Sales',
}