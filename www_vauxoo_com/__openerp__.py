# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Vauxoo
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Vauxoo Site',
    'version': '0.4',
    'category': 'Vauxoo',
    'summary': 'Module to stablish the base for development on our website',
    'complexity': 'easy',
    'description': """
Web Site: www.vauxoo.com
========================

This module has the intention to build automatically all the vauxoo site,
The main objective is to have all the technical information necesary to build
the web-site mixing all necesary Github repositories.

Necesary Github repositories to comply with dependencies.

- 0 https://github.com/Vauxoo/addons-vauxoo/ #migration to V8 not started yet [delete repo and reconvert] - ?
- 1 https://github.com/Vauxoo/hideleftmenu #missing some forks to origin web_addons - nhomar
- 2 https://github.com/vauxoo-dev/cms #WIP branch 8.0 - oscar
- 3 https://github.com/vauxoo-dev/autodoc #not migrated yet - ? [Possibly complete depreciation]

Dependencies and why:

**contpaq_openerp_vauxoo:** activate the service to upload contpaq databases
    and propose them to be migrated. #TODO: think where should go commented for now.

**website_blog:** activate the blog page and the main API.
**website_event:** activate the events page.
**website_sale:** activate the products page and the e-commerce platform.
**website_project:** activate the public projects page.
**theme_vauxoo:** Improve the styles in all odoo, must install and select the theme.
**website_crm:** This simple application integrates a contact form in your
    "Contact us" page. Forms submissions create leads automatically in Odoo CRM..
**web_doc:** Enable Help button.
    """,
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
    'js': [
        'static/src/js/www_vauxoo_com.js',
    ],
    'qweb': [
    ],
}
