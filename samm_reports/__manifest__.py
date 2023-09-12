{
    'name': 'SAMM Reports',
    'version': '15.0.1',
    'category': '',
    'summary': 'SAMM-Reports',
    
    'author': 'SSL',
    'website': '',
    'maintainer': '',

    'depends': ['base','sale','saam_extension','stock','purchase'],
    'data': [
    'reports/sale_report.xml',
    'reports/sale_report_templates.xml',
    'reports/delivery_slip.xml',
    'reports/stock_report_views.xml',
    'reports/purchase_reports.xml',
    'reports/report_deliveryslip.xml',
    'reports/account_report.xml',
    'reports/report_invoice.xml',
    'reports/report_stockpicking_operations.xml',
    'reports/report_purchase_order.xml',

    ],

    
    'installable': True,
    'auto_install': False,
    'price': 110.00,
    'currency': 'EUR',
    # 'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
}