{
    'name': 'Samm Extension',
    'version': '15.0.1',
    'category': '',
    'summary': 'Saam Extension',
    
    'author': 'SSL',
    'website': '',
    'maintainer': '',

    'depends': ['base','product','sale_management','account', 'stock', 'sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/sequence.xml',
        # 'data/mail_template.xml',
        # 'data/ir_cron_data.xml',
        'views/custom_salesperson.xml',
        'views/partner.xml',
        'views/product.xml',
        'views/res_company.xml',
        'views/invoice_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'price': 110.00,
    'currency': 'EUR',
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
}
