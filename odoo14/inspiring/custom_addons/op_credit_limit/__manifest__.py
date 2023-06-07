# -*- coding: utf-8 -*-
{
    'name': "Customer Credit Limit",
    'summary': """
        Customer Credit Limit
        """,
    'description': """
        Customer Credit Limit,
    """,
    'author': "Odoo Pro 365",
    'website': "https://www.odoopro365.com",
    'category': 'Sales/Sales',
    'version': '14.0.1',
    'depends': ['base', 'account', 'sale_management', 'contacts', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        #data
        'data/sequence.xml',
        'data/credit_attachment_list.xml',
        #views
        'views/op_partner.xml',
        # 'views/op_sale.order.xml',
        'views/op_credit_request.xml',
        'views/hr_employee.xml',

        #reports
        'reports/credit_request.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        "static/src/xml/buttons.xml",
    ],
    "images": ["static/description/background.png", ],
    # "live_test_url": "",
    'application': True,
    "auto_install": False,
    "installable": True,
    "price": 20,
    "currency": "EUR",
    'license': 'OPL-1',

}
