# -*- coding: utf-8 -*-
{
    'name': "Bank Statement Reconciliation Custom",

    'summary': 'modify filter in the payment search view to show child of partner or parent of partner',
    
    'description' : """
        * modify filter in the payment search view to show child of partner or parent of the partner
    """,

    "author": "Openinside",
    "license": "OPL-1",
    'website': "https://www.open-inside.com",
    "price" : 0,
    "currency": 'EUR',
    'category': 'Accounting',
    'version': '15.0.1.1.4',

    # any module necessary for this one to work correctly
    'depends': ['oi_bank_reconciliation'],

    # always loaded
    'data': [
        'views/account_payment.xml',       
    ],    
    'odoo-apps' : False,
    'auto_install': False,
    'images': [
    ],    
}