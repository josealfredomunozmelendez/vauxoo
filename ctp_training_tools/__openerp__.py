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
    'name': 'CTP tools',
    'version': '0.1',
    'category': 'Vauxoo Ondemmand',
    'complexity': 'easy',
    'description': """
Web Site: www.vauxoo.com
========================

This module has the intention of automate some needs related to CTP training.

1.- Add a certificate field for users which 
1.- Add a security rule to trat this information. 
    """,
    'depends': [
        'mail',
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
    ],
    'js': [
    ],
    'qweb': [
    ],
}
