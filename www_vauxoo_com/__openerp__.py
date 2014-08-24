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
    'name': 'Vauxoo Site Build Module',
    'version': '0.1',
    'category': 'Vauxoo Ondemmand',
    'complexity': 'easy',
    'description': """
Web Site: www.vauxoo.com
========================

This module has the intention to build automatically all the vauxoo site,
The main objective is to have all the technical information necesary to build
the web-site mixing all necesary Github repositories.

Necesary Github repositories to comply with dependencies.

- 0 https://github.com/Vauxoo/addons-vauxoo/
- 1 https://github.com/Vauxoo/hideleftmenu
- 2 https://github.com/vauxoo-dev/cms
- 3 https://github.com/vauxoo-dev/autodoc
- 4 https://github.com/odoo/odoo-extra
- 5 https://github.com/Vauxoo/design-themes

Dependencies and why:

**contpaq_openerp_vauxoo:** activate the service to upload contpaq databases
and propose them to be migrated.

**website_blog:** activate the blog page and the main API.
**website:** activate the home page and the whole structure of the website
**website_event:** activate the events page.
**website_sale:** activate the products page and the e-commerce platform.
**website_project:** activate the public projects page.
**runbot:** activate the runbot page to test odoo.
**theme_vauxoo:** Improve the styles in all odoo, must install and select the theme.
**website_crm:** This simple application integrates a contact form in your
    "Contact us" page. Forms submissions create leads automatically in Odoo CRM..
**web_doc:** Enable Help button.
    """,
    'depends': [
                'website',
                #'runbot',
                'website_vauxoo_home',
                'website_sale',
                'website_blog',
                'website_event',
                'website_project',
                'website_hr_recruitment',
                'website_event_track',
                'website_crm',
                'website_forum_doc',
                #'web_doc',
                #'hr_attendance',
                #'ctp_training_tools',
                'theme_zen',
                #'contpaq_openerp_vauxoo', Commented until it is stable.
                ],
    'author': 'Vauxoo',
    'data': [
    ],
    'test': [
        #'test/contact_form.yml', #TODO This module should have all tests for the site.
    ],
    'installable': True,
    'auto_install': False,
    'css': [
        'static/src/css/vauxoo.css',
    ],
    'js': [
        'static/src/js/www_vauxoo_com.js',
    ],
    'qweb': [
        'static/src/xml/base.xml',
    ],
}
