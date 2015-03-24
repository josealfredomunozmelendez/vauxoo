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

from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _
from openerp import tools
from openerp import tests
from openerp.osv import osv
from openerp import netsvc
import openerp
from report_webkit import webkit_report


import logging
_logger = logging.getLogger(__name__)


class sale_order_vauxoo_report_html(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_order_vauxoo_report_html, self).__init__(
            cr, uid, name, context=context)

webkit_report.WebKitParser('report.sale.order.vauxoo.webkit',
                           'sale.order',
                           'addons/sale_order_vauxoo_report_webkit/report/sale_order_vauxoo_report_html.mako',
                           parser=sale_order_vauxoo_report_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
