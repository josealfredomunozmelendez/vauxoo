# coding: utf-8
from __future__ import division

from odoo import fields, models, api


class AccountBudget(models.Model):
    _inherit = "crossovered.budget"

    use_cost = fields.Boolean(
        help="Used to compute costs on employees "
             "(Dates matter to be used)"
    )
    rate_usd = fields.Float(
        default=1.0,
        help="The conversion analysis is never the real one, then "
             "with this we can have an amount in th company currency "
             "and then properly exchange to usd using this factor as a "
             "reference always then with the execution we can see what "
             "was the real amount in usd."
    )
    color = fields.Integer()

    _sql_constraints = [
        ('rate_usd_exist',
         'CHECK (rate_usd>=0.0)',
         'A negative or zero rate does not make sense please try a proper '
         'value.')
    ]


class AccountBudgetLine(models.Model):
    _inherit = "crossovered.budget.lines"

    description = fields.Char()
    amount_usd = fields.Float(
        compute="_compute_amount_usd",
        help="Amount in usd, this will always be used to analyze with "
             "the employees behavior (TODO: make it configurable) "
    )

    @api.depends('planned_amount')
    @api.multi
    def _compute_amount_usd(self):
        for line in self:
            amount = round(
                line.planned_amount/line.crossovered_budget_id.rate_usd, 2)
            line.amount_usd = amount
