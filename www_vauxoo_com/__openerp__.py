# -*- coding: utf-8 -*-
{
    'name': 'Vauxoo Site',
    'version': '0.6',
    'category': 'Vauxoo',
    'summary': 'Module to stablish the base for development on our website',
    'complexity': 'easy',
    'depends': [
        'website_vauxoo',
        # Tools necesary to work with this enviroment.
        'admin_technical_features',
    ],
    'author': 'Vauxoo',
    'data': [
        'data/oauth_data.xml',
        'data/set_configuration.yml',
        'data/lang.xml',
        'views/layout.xml',
        'views/login_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'css': [
    ],
    'qweb': [
    ],
}
