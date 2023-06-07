# -*- coding: utf-8 -*-
{
    "name": "Sales Margin Report || Product Margin Report",
    "author": "OMAX Informatics",
    "version": "14.0.1.0",
    "website": "https://www.omaxinformatics.com",
    "category": "Sales,Warehouse",
    'description' : """
        This Odoo app helps to print Sales Margin Report in Excel & PDF.
    """,
    'summary': """
        Sale Margin Report,
        Sales Margin Report,
        Product Margin Report,
        Product Sale Margin Report,
        Product Sales Margin Report,
        Margin Report,
        Sales Profit Report,
        Sale Profit report,
        Sale Profitability Report,
        Sales Profitability Report,
        Profit & Loss Report,
        Profit and Loss Report,
        Cost Price,
        Sales Margin & Analysis Report,
        Sales Margin and Analysis Report
        Product Profitability Report,
	""",
    "depends": ["sale","sale_management","sales_team"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/sale_margin_report_wizard_view.xml",
        "report/sales_margin_report_template.xml",
    ],
    'demo': [],
    'test':[],
    "images": ["static/description/banner.jpg",],
    'license': 'AGPL-3',
    'currency':'USD',
    'price': 30.0,
    'qweb': [
        'static/src/xml/pos_pl_report.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
