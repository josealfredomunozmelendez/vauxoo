# -*- coding: utf-8 -*-
{
    'name': 'Vauxoo Site',
    'version': '0.6',
    'category': 'Vauxoo',
    'summary': 'Module to stablish the base for development on our website',
    'complexity': 'easy',
    'depends': [
        'website_vauxoo',
        'website_blog',
        'website_crm',
        'website_event',
        'website_event_track',
        'website_hr_recruitment',
        'website_forum_doc',
        'website_sale',
        'website_project',
        'website_variants_extra',
        'auth_oauth',
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
