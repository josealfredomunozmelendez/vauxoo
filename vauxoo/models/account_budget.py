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
    cost_share = fields.Float(
        default=0.0,
        help="Percentage that this budget represent of the total "
             "Employee costs."
    )
    budget_income = fields.Float(
        default=0.0,
        help="Amount of income earned in this budget."
    )
    budget_expense = fields.Float(
        default=0.0,
        help="Amount of expense spent in this budget."
    )
    executed_income = fields.Float(
        default=0.0,
        help="Amount of income executed in this budget."
    )
    executed_expense = fields.Float(
        default=0.0,
        help="Amount of expense spent in this budget."
    )
    cost_per_hour = fields.Float(
        default=0.0,
        help="Cost of Employee per hour."
    )
    employee_cost = fields.Float(
        default=0.0,
        help="Amount of Employee Costs in the company."
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
