# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
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
#
{
    "name": "Facturae Test CFDI",
    "version": "1.0",
    "depends": [
        "base",
        "account",
        "product",
        "l10n_mx_partner_address",
        "l10n_mx_facturae_pac_sf",
    ],
    "author": "Vauxoo",
    "description": """
Facturae Test CFDI
==================

This wizard execute test yaml of electronic invoice CFDI "N" times. 
This with finally of make test to the server.
    """,
    "website": "http://vauxoo.com",
    "category": "Addons Vauxoo",
    "data": [
        'wizard/facturae_test_wizard.xml',
    ],
    "test": [],
    "active": False,
    "installable": True,
}
