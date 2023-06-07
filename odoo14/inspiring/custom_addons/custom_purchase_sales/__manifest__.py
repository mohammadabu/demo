{
    "name": "Custom Purchase & Sales Orders",
    "description": """Shows total of Customer Invoice Amount in Sales Order and total of vendor bills amount in 
    purchase order""",
    "author": "Peerless Technologies",
    "version": "1.0",
    'license': 'OPL-1',
    "depends": ["purchase", "sale_management"],
    "init_xml": [],
    "data": [
             'views/view_purchase_order.xml',
             'views/view_sale_order.xml'
    ],
    "demo_xml": [],
    "installable": True, 
}
