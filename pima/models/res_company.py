# coding: utf-8
from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    def _compute_add(self):
        self.website_address_ids = self.sudo().partner_id.child_ids

    website_address_ids = fields.Many2many('res.partner',
                                           string='Web Contacts',
                                           compute='_compute_add',
                                           store=False,
                                           help="All contact public Contacts"
                                           "to be shown in contact form.")
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        related='country_id.currency_id',
    )
