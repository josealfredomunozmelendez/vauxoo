# coding: utf-8
from odoo import models, fields, api
from . import rst2html


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    desc2html = fields.Text(string="Converted RST", compute="_rst2html")

    @api.depends('name')
    def _rst2html(self):
        for line in self:
            line.desc2html = rst2html.html.rst2html(line.name)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    note2html = fields.Text(string="Converted RST", compute="_rst2html")

    @api.depends('note')
    def _rst2html(self):
        for sale in self:
            sale.note2html = rst2html.html.rst2html(sale.note)


class SalesChannel(models.Model):

    _inherit = "crm.team"

    address_id = fields.Many2one(
        'res.partner',
        string="Address to show in the Header of the sale Order")
