# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Print Invoices',
    'version': '14.0.1.0.0',
    'category': 'Invoicing',
    'summary': 'Print Invoice For all users',
    'description': "",
    'author': "techsfactory",
    'depends': ['account'],
    "license": "AGPL-3",
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/printInvoices.xml',
    ],
    "images": ['static/description/banner.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
