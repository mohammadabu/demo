# -*- coding: utf-8 -*-
{
'name': 'Purchase Order Workflow',
'summary': 'Purchase Order Workflow, Highly Configurable and Flexible approval '
           'cycle/process for purchase orders, Purchase Approval, PO Approval Process, '
           'Approval Cycle, Approval Process, Purchase Order, Approval Workflow, Approve '
           'Purchase Order, Approve PO, Purchase Manager, Multi-level Approval Process, '
           'Purchase Approval Flow, Approval Rules, Manager Approval',
'version': '14.0.1.1.2',
'category': 'Purchases',
'website': 'https://www.open-inside.com',
'description': '''
		Purchase Order Workflow
		 
    ''',
'images': ['static/description/cover.png'],
'author': 'Openinside',
'license': 'OPL-1',
'price': 9.99,
'currency': 'EUR',
'installable': True,
'depends': ['purchase', 'oi_workflow'],
'data': ['data/approval_config.xml', 'views/purchase_order.xml'],
'uninstall_hook': 'uninstall_hook',
'odoo-apps': True,
'application': False
}