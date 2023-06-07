# -*- coding: utf-8 -*-
{
    'name' : 'Petty Cash Management',
    'version': '14.0.1.0',
    'category': 'Accounting',
    'summary': 'Petty Cash Management',
    'description': """Petty Cash Management.""",
    'author': "McGeorge Consulting LTD.",
    'support':'info@mcgeorgeconsulting.com',
    'website': 'www.mcgeorgeconsulting.com',
    'currency': 'USD',
    'price': 80.0,
    'license': 'OPL-1',
    'images': ["static/description/banner.png"],
    'depends' : ['account'],
    'data': [
          'security/cash_register_security.xml',
          'security/ir.model.access.csv',
          'views/account_bank_statement_view.xml', 
          'views/account_reconsilation_template.xml',
          'views/account_bank_statement_line_view.xml',
          'views/account_payment_view.xml',
          'views/report_statement.xml',
          'data/account_data.xml',
          'views/company_view.xml',   
        ],
    
    'qweb': [
        "static/src/xml/account_reconciliation.xml",
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
