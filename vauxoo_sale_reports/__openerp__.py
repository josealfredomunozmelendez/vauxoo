# coding: utf-8
{
    'name': 'Vauxoo Report',
    'version': '0.6',
    'category': 'Vauxoo',
    'depends': [
        'city',  # l10n_mx should depends of it
        'website_report',  # Horizontal references dependency sucks.
                 # It is on odoo-mexico-v2.
        'sales_team',  # Because we need to be supported by the section_id to
                       # print where the Sale order is being printed from.
        'sale_stock',
        'l10n_mx_partner_address',
    ],
    'author': 'Vauxoo',
    'data': [
        'view/vauxoo_report_sale.xml',
        'view/layout.xml',
        'view/sale_view.xml',
        'data/set_configuration.yml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
