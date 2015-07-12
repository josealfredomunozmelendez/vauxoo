# -*- coding: utf-8 -*-
from openerp import models, fields, osv
from . import rst2html


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _rst2html(self):
        self.note2html = rst2html.html.rst2html(self.note)

    note2html = fields.Text(string="Converted RST", compute="_rst2html")
