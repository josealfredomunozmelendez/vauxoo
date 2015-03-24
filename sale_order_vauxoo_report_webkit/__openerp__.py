# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Jorge Angel Naranjo Rogel (jorge_nr@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
############################################################################
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
    "name": "Sale Order Vauxoo Report Webkit",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Sale",
    "description": """
Sale Order Vauxoo Report Webkit
===============================

This module add sale order report for Vauxoo Company in format webkit.

This module l10n_mx_partner_address will found in this branch: 

    lp:vauxoo-private/openerp-mexico-localization-autonomy-v2


    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": ["sale", "l10n_mx_partner_address"],
    "demo": [],
    "data": [
        "data/data.xml",
        "sale_order_vauxoo_report_webkit.xml",
    ],
    "installable": True,
    "active": False,
}
