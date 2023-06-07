# -*- coding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 WebLine Apps 
##############################################################################

{
    'name': 'Hide Cost Price Product',
    'version': '14.0.1.0',
    'category': 'product',
    'description': """
        Hide Cost Price Product, display only allow user 
    """,
    'summary': """
        Hides Product Cost Price, 
        display only allow user
        #################################################### 
        ####################################################    

        This odoo apps provide hide cost price and see particular user.
        user to hide cost price from particular product.
        this odoo apps provide best feature to hide product cost price.
    """,
    'author': 'Weblineapps',
    'website': 'weblineapps@gmail.com ',
    'depends': ['sale'],
    'data': [
        'security/security.xml',
        'views/product_templet_view.xml',
    ],
    'price': 5.00,
    'images' : ['static/description/banner.png'],
	'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
