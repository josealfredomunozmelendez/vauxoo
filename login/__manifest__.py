# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo Web Login Screen
#    Copyright (C) 2016- XUBI.ME (http://www.xubi.me)
#    @author binhnguyenxuan
#    (https://www.linkedin.com/in/binh-nguyen-xuan-46556279)

{
    'name': 'Odoo Web Login Screen',
    'summary': 'The new configurable Odoo Web Login Screen',
    'version': '10.0.1.0',
    'category': 'Website',

    'author': "binhnguyenxuan (www.xubi.me)",
    'website': 'http://www.xubi.me',
    'license': 'AGPL-3',
    'depends': [
        'web',
        'website',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'templates/webclient_templates.xml',
        'templates/website_templates.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
