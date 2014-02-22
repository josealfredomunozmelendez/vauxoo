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
the web-site mixing all necesary branches.

Branches necesary to comply with dependencies.

- 0 lp:openobject-addons/7.0
- 1 lp:~vauxoo/web-addons/7.0-web_hideleftmenu 
- 2 lp:vauxoo-private/cms
- 3 lp:vauxoo-private/autodoc
- 4 lp:addons-vauxoo/7.0

Dependencies and why:

**contpaq_openerp_vauxoo:** activate the service to upload contpaq databases
and propose them to be migrated.

**portal_news:** activate the blog page and the main API.
**portal_home:** activate the home page.
**portal_events:** activate the events page.
**portal_products:** activate the products page.
**portal_project_imp:** activate the event page.
**portal_runbot:** activate the runbot page to test openerp.
**web_vauxoo_cust:** Improve the styles in all openerp and login page.
**portal_crm_vauxoo:** Improve the contact form and manage the captcha widget on it.
**web_doc:** Enable Help button.
    """,
    'depends': [
                'portal_home',
                'portal_runbot',
                'portal_products',
                'portal_events',
                'portal_project_imp',
                'portal_hr_imp',
                'web_vauxoo_cust',
                'portal_crm_vauxoo',
                'portal_public_documents',
                'web_doc',
                #'web_allow_custom_root',#Branch 7.0-web_hideleftmenu disable because web_export_view make errors
                # Because the little button TODO: Create 2 modeules www and erp dependencies should be differents
                'hr_attendance', 
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
