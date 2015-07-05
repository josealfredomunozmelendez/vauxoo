# -*- coding: utf-8 -*-
{
    'name': 'Vauxoo Report',
    'version': '0.6',
    'category': 'Vauxoo',
    'description': '''
Quotation Report
    ''',
    'depends': [
        'sale',
        'sale_stock',
        'l10n_mx_partner_address',
    ],
    'author': 'Vauxoo',
    'data': [
        'view/vauxoo_report_sale.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
