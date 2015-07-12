# -*- coding: utf-8 -*-
from openerp import models, fields, api
from . import rst2html


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.one
    @api.depends('name')
    def _rst2html(self):
        self.desc2html = rst2html.html.rst2html(self.name)

    desc2html = fields.Text(string="Converted RST", compute="_rst2html")

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('note')
    def _rst2html(self):
        self.note2html = rst2html.html.rst2html(self.note)

    note2html = fields.Text(string="Converted RST", compute="_rst2html")
