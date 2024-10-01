# -*- coding: utf-8 -*-
{
    'name': 'Odoo Direct Print to Printer',
    'version': '16.0',
    'category': 'Generic Modules',
    'summary': 'Odoo Direct Print to Printer',

    'depends': ['web'],

    'data': [
    ],

    'assets': {
        'web.assets_backend': [
            'odoo_direct_to_printer/static/src/js/*.js'
        ],
        'web.assets_common': [
            'odoo_direct_to_printer/static/src/css/print_min.css',
        ],
        'web.assets_qweb': [
            'odoo_direct_to_printer/static/src/xml/*.xml',
        ],
    },

    'images': ['static/description/odoo_direct_print_banner.png'],

    'author': 'TeqStars',
    'website': 'http://teqstars.com/r/bSq',
    'support': 'support@teqstars.com',
    'maintainer': 'TeqStars',

    "description": """
        - Print management
        - Printing solution
        - Direct printing
        - Direct print
        - Printing integration
        - Local printing
        - Odoo print direct to printer
        - base report print
        - report print
        - print report
        - Printing optimization
        """,

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    "price": "39.99",
    "currency": "EUR",
}
