# -*- coding: utf-8 -*-
{
'name': 'Purchase Requisition Workflow',
'summary': 'Purchase Requisition Workflow, Highly Configurable and Flexible approval '
           'cycle/process for purchase Requisitions, Purchase Approval, PR Approval '
           'Process, Approval Cycle, Approval Process, Purchase Requisition, Approval '
           'Workflow, Approve Purchase Requisition, Approve PO, Purchase Manager, '
           'Multi-level Approval Process, Purchase Approval Flow, Approval Rules, '
           'Manager Approval',
'version': '14.0.1.1.5',
'category': 'Purchases',
'website': 'https://www.open-inside.com',
'description': '''
		Purchase Requisition Workflow
		 
    ''',
'images': ['static/description/cover.png'],
'author': 'Openinside',
'license': 'OPL-1',
'price': 9.99,
'currency': 'EUR',
'installable': True,
'depends': ['purchase_requisition', 'oi_workflow'],
'data': ['data/approval_config.xml', 'views/purchase_requisition.xml'],
'uninstall_hook': 'uninstall_hook',
'odoo-apps': True,
'application': False
}