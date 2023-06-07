# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Auto Credit Note from Return Delivery/Products",
    'version': "14.0.0.1",
    'category': "Invoicing",
    'summary': "Product Return with Credit Note from return product auto refund from return auto invoice refund from return products refund process from delivery return refund invoice from return picking auto generate refund from return goods create refund from return DO",
    'description': """This odoo app helps user to return delivery order for selected product with customer credit note for invoice, User can return delivery order for product, create and link draft customer credit note with incoming transfer for validated invoice.""",
    'author': "BrowseInfo",
    "website": "https://www.browseinfo.in",
    "price": 69,
    'currency': "EUR",
    'depends': ['delivery'],
    'data': ['security/ir.model.access.csv',
             'wizard/return_picking_reversal_views.xml',
             'wizard/stock_picking_return_views.xml',
             'views/stock_picking_views.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
    "live_test_url": 'https://youtu.be/5iNemoWFcXE',
    "images":["static/description/Banner.png"],
}
