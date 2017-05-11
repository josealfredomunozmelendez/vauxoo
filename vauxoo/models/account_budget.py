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
        compute='_compute_amount',
        help="Amount of income earned in this budget."
    )
    budget_expense = fields.Float(
        compute='_compute_amount',
        help="Amount of expense spent in this budget."
    )
    executed_income = fields.Float(
        compute='_compute_amount',
        help="Amount of income executed in this budget."
    )
    executed_expense = fields.Float(
        compute='_compute_amount',
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
    planned_amount = fields.Float(
        compute='_compute_amount',
        help='Planned Amount for this Budget'
    )
    practical_amount = fields.Float(
        compute='_compute_amount',
        help='Practical Amount for this Budget'
    )
    theoretical_amount = fields.Float(
        compute='_compute_amount',
        help='Theoretical Amount for this Budget'
    )
    color = fields.Integer(
        help="Color"
    )

    _sql_constraints = [
        ('rate_usd_exist',
         'CHECK (rate_usd>=0.0)',
         'A negative or zero rate does not make sense please try a proper '
         'value.')
    ]

    @api.depends()
    def _compute_amount(self):
        for budget in self:
            planned_amount = 0.0
            practical_amount = 0.0
            theoretical_amount = 0.0
            budget_income = 0.0
            budget_expense = 0.0
            executed_income = 0.0
            executed_expense = 0.0
            for cbl in budget.crossovered_budget_line:
                planned = cbl.planned_amount
                practical = cbl.practical_amount
                planned_amount += planned
                practical_amount += practical
                theoretical_amount += cbl.theoritical_amount
                budget_income += planned if planned > 0 else 0
                budget_expense += planned if planned < 0 else 0
                executed_income += practical if practical > 0 else 0
                executed_expense += practical if practical < 0 else 0
            budget.update(dict(
                planned_amount=planned_amount,
                practical_amount=practical_amount,
                theoretical_amount=theoretical_amount,
                budget_income=budget_income,
                budget_expense=budget_expense,
                executed_income=executed_income,
                executed_expense=executed_expense,
            ))


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
