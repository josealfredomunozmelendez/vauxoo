# -*- coding: utf-8 -*-
{
    'name': 'Vauxoo Report',
    'version': '0.6',
    'category': 'Vauxoo',
    'description': '''
Quotation Report
</template>
    <!-- Remove conflicting style -->
    <xpath expr="//head/link[@href='/web/static/src/css/full.css']" position="replace"></xpath>

    ''',
    'depends': [
        'sale',
        'sale_stock',
        'l10n_mx_partner_address',
    ],
    'author': 'Vauxoo',
    'data': [
        'view/vauxoo_report_sale.xml',
        'view/layout.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
