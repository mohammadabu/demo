# -*- coding: utf-8 -*-
##########################################################################
# Author      : Kanak Infosystems LLP. (<https://www.kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.kanakinfosystems.com/license>
##########################################################################
{
    'name': 'Customer Statement Report',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': "This module allows us to print or send reports of individual and all customers. We can view details of multiple customers at the same time and can also apply date filters. | Customer Statement | Vendor statement | Schedule Statement | Send Statement | Email Statement",
    'description': """
Customer Statement Report module is used to Print and Send Individual or all Customer's Statement.
====================================================================================
    """,
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_qweb.xml',
        'report/report_view.xml',
        'views/statement_view.xml',
        'views/res_config_settings_views.xml',
        'wizard/customer_statement_wizard.xml',
        'data/mail_template_data.xml',
        'data/data.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'sequence': 1,
    'installable': True,
    'price': 30,
    'currency': 'EUR',
    'live_test_url': 'https://www.youtube.com/watch?v=SbZYbNjk-2Q',
}
