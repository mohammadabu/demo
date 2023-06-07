{
    'name': "custom_invoice_template",
    'author': "Techs Factory",
    'website': "https://www.techsfactory.com",
    'version': '0.1.1',
    'depends': ['base','web','account','custom_company_info'],
    'data': [
        'views/templates.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.report_assets_common': [
            'custom_invoice_template/static/src/scss/style.scss',
            'custom_invoice_template/static/src/less/font.less',
        ],
    }
}