# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
    "name": "Creacion del Reporte de Factura Electronica para Mexico",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Localization/Mexico",
    "description" : """This module adds a report to electronic invoice, 
        this includes report to cfd, cfdi and cbb customized to Vauxoo.
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": ["l10n_mx_facturae_report"],
    "demo": [],
    "data": [
        "data.xml",
        "l10n_mx_facturae_report_webkit.xml",
    ],
    "installable": False,
    "active": False,
}
