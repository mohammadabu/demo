#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Opening Balance',
    'category': 'Account',
    'author': 'VPerfectcs',
    'version': '14.0.1.0.0',
    'website': 'https://www.vperfectcs.com',
    'description': """
    Opening Balance For Partner Account.
    """,
    'depends': [
    'account'
    ],
    'data': [
    'security/ir.model.access.csv',
    'data/seq.xml',
    'wizard/cancel_wizard.xml',
    'views/partner_account.xml',

    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'price' : 49,
    'currency' : 'EUR',
}
