{
    'name': 'Product Damage Report',
    'version': '1.0',
    'summary': 'Product Damage Report',
    'description': """
        To print a report products which are expiring
    """,
    'category': 'General',
    'author': 'Techs Factory',
    'currency': 'EUR',
    'depends': ['stock', 'base', 'product'],
    'images': ['static/description/product_damage_report_filter_data_wizard.png'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/grp_category_product_damage_report_template.xml',
        'wizard/product_damage_report_wizard_view.xml',
        'views/product_damage_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}