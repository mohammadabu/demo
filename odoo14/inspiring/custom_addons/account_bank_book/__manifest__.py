# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Mashood K.U(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

{
    'name': 'Bank Book Report',
    'version': '14.0.1.0.0',
    'summary': """Generates bank book report in both PDF and XLSX formats.
                It is a subsidiary book which helps in checking the bank balances at any point of time. """,
    'description': """Generates bank book report in both PDF and XLSX formats,Detailed bank book report,
                    checking the bank balances,Exporting the bank book report to Excel and PDF Format,
                    banking transactions,Accounting,Accounting XLSX Report,Accounting PDF report,
		            Report Exporting,Accounting module,Odoo 13 Accounting.""",
    'category': 'Accounting',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['base_accounting_kit'],
    'website': 'https://www.cybrosys.com',
    'live_test_url': 'https://www.youtube.com/watch?v=yEdZtUDHxuM',
    'data': [
        'wizard/account_bank_book_report_wizard.xml', 
        'views/action_manager.xml',
    ],
    'qweb': [],
    'images': ['static/description/banner.png'], 
    'license': 'OPL-1',
    'price': 9.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False, 
}
