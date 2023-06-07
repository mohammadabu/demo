# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "Recurring Documents",

    'summary': "Mixin for recurring Documents",
    'author': 'Maik Steinfeld',
    'website': "https://www.steinfeld.one",
    'category': 'Extra',
    'version': '14.0.2.3.0',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        
        'data/recurring_document_subscription_data.xml',
        
        'views/menu.xml',
        'views/recurring_document_config_views.xml',
        'views/recurring_document_subscription_views.xml',
    ],
    'demo': [
    ],
    'images':[
        'images/module_image.png',
        ],
    'installable': True,
    'price': 49.00,
    'currency':'EUR',
    'license':'OPL-1',
    'support':'entwicklung@steinfeld.one',
    'sequence':200,
}
