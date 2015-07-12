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
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
