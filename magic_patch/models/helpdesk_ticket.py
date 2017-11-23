# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def _default_team_id(self):
        return False

    team_id = fields.Many2one(
        'helpdesk.team', string='Helpdesk Team', default=False, index=True)
