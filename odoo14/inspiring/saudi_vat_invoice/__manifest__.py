# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

{
    'name': 'Saudi VAT Invoice /Saudi E-Invoice /Saudi Electronic Invoice',
    'version': '14.0.1.5',
    'sequence': 1,
    'category': 'Accounting',
    'summary': 'Saudi VAT Invoice / E-Invoice / Saudi Electronic Invoice / Electronic Invoice KSA',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'price': 20,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """
Saudi VAT Invoice / E-Invoice / Saudi Electronic Invoice / Electronic Invoice KSA
        """,
    'depends': ['web','account', 'sa_uae_vat','etmam_font','custom_company_info'],
    'data': [
        # 'views/assets.xml',
        'report/saudi_report_layout.xml',
        'report/saudi_vat_invoice_report_template.xml',
        'report/saudi_vat_invoice_report.xml',
        'report/saudi_report_layout_branch.xml',
        'views/vat_invoice_view.xml',
        'views/res_config_settings_view.xml',
        'report/saudi_vat_simplified_tax_invoice_report.xml',

    ],
    'images': ['images/main_screenshot.gif','images/logo.png','images/background.png','static/description/logo.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
