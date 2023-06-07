# -*- coding: utf-8 -*-
{
    'name': 'Sales receipt',
    'summary':"""This module create a summary of the sales report""",
    'depends': ['sale_management'],
    'version': '14.0.0.1.0',
    'category': 'sale',
    'author':'SARL FOCUS SYSTEM.',
    'maintainer': 'SARL FOCUS SYSTEM.',
    'contributors':['contact <contact@focussystem.dz>'],
    'website':'http://www.focussystem.dz',
    'data':[        
        'report/sales_receipt.xml',
        'report/report_Commande.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application':True,
    'images': ['static/description/poster_image.png'],
}
