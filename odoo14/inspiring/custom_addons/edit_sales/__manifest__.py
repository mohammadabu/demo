{
    'name': 'Edit Sales',
    'description': 'Custom addon to modify Sales',
    'author': 'Techs Factory',
    'version': '1.0',
    'depends': ['base', 'sale_management', 'sale'],
    'data': [
        'views/edit_sales.xml',
        'security/security.xml',
        'reports/edit_quotation_order.xml',
        'security/ir.model.access.csv',
        ]
}