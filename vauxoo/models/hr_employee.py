# coding: utf-8
from __future__ import division
from datetime import datetime, timedelta, date

from odoo import fields, models, api, _


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


class HrJob(models.Model):

    _inherit = "hr.job"

    wage = fields.Float(
        track_visibility='onchange',
        help="Conceptual wage this job should win (to planning purposes)")
    theoretical_timesheet = fields.Float(
        default=100.00,
        track_visibility='onchange',
        help="Manually computed value to take know how is the effective of "
             "this person in terms of timesheet use 120 for a great resource "
             "10 for a newbie")


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    salary_on_job = fields.Float(
        store=True,
        track_visibility='onchange',
        compute='_compute_total_salary',
        inverse='_inverse_total_salary',
        help="Salary conceptual on job")
    total_salary = fields.Float(
        store=True,
        track_visibility='onchange',
        compute='_compute_total_salary',
        inverse='_inverse_total_salary',
        help="How much it is costing after payroll comes in, USD")
    perceived_salary = fields.Float(
        help="How much this person is receiving monthly, USD")
    theoretical_cost = fields.Float(
        compute="_compute_cost",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    current_cost = fields.Float(
        compute="_compute_cost",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    billable_cost = fields.Float(
        compute="_compute_cost",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    theoretical_timesheet = fields.Float(
        track_visibility='onchange',
        help="Manually computed value to take know how is the effective of "
             "this person in terms of timesheet use 120 for a great resource "
             "10 for a newbie")
    is_cost = fields.Boolean(
        track_visibility='onchange',
        help="This employee is a cost or an expense?")
    generate_income = fields.Boolean(
        track_visibility='onchange',
        help="It is an direct income generator (True) or a passive "
             "generator (False)")
    hours_invoice = fields.Float(
        compute='_compute_timesheet_average',
        help="How many hours this person is being reporting")
    hours_informed = fields.Float(
        compute='_compute_timesheet_average',
        help="How many hours this person is having billable")

    @api.multi
    def _inverse_total_salary(self):
        for emp in self:
            if emp.contract_id:
                emp.contract_id.wage = emp.total_salary
                continue
            struct = self.env['hr.payroll.structure'].search([], limit=1).id
            self.env['hr.contract'].create({
                'name': _('Created from employee'),
                'employee_id': emp.id,
                'wage': emp.total_salary,
                'struct_id': struct,
                'date_start': datetime.strftime(date.today(), '%Y-%m-%d')
            })
            emp.write({
                'salary_on_job': emp.salary_on_job,
            })

    @api.depends('is_cost', 'contract_id', 'job_id.wage')
    def _compute_total_salary(self):
        for emp in self.filtered(lambda e: e.contract_id):
            emp.update(dict(total_salary=emp.contract_id.wage,))
        for emp in self.filtered(lambda e: e.job_id):
            emp.update(dict(salary_on_job=emp.job_id.wage,))

    @api.depends('total_salary', 'theoretical_timesheet', 'is_cost')
    def _compute_cost(self):
        employees_cost = self.search([('is_cost', '=', True)])
        employees_generate = self.search([('generate_income', '=', True)])
        budgets = self.env['crossovered.budget'].search(
            [('use_cost', '=', True), ('state', 'in', ['confirm'])])
        theoretical = sum(employees_cost.mapped('total_salary'))
        salaries = sum(employees_cost.mapped('salary_on_job'))
        hours = sum(employees_generate.mapped('theoretical_timesheet'))
        hours_real = sum(employees_generate.mapped('hours_invoice'))
        hours_billable = sum(employees_generate.mapped('hours_invoice'))
        budgeted = -sum(budgets.mapped('crossovered_budget_line').filtered(
            lambda line: line.planned_amount < 0.0).mapped('amount_usd'))
        cost = hours and float((theoretical + budgeted) / hours) or 0.00
        cost_real = hours_real and float((salaries + budgeted)/hours_real)
        cost_billable = hours_real and float(
            (salaries + budgeted)/hours_billable)
        res = {
            'theoretical_cost': cost,
            'current_cost': cost_real,
            'billable_cost': cost_billable,
        }
        self.filtered(lambda emp: emp.generate_income).update(res)

    @api.depends('user_id', 'total_salary')
    def _compute_timesheet_average(self):
        timesheets = self.env['account.analytic.line']
        today = date.today() - timedelta(days=30)
        end_date = last_day_of_month(today)
        start_date = today.replace(day=1)
        end_date = datetime.strftime(end_date, '%Y-%m-%d')
        start_date = datetime.strftime(start_date, '%Y-%m-%d')
        for emp in self.filtered(lambda e: e.user_id):
            domain = [('user_id', '=', emp.user_id.id),
                      ('date', '<=', end_date),
                      ('date', '>=', start_date)]
            results = timesheets.search(domain)
            res = {
                'hours_invoice': sum(results.mapped('invoiceables_hours')),
                'hours_informed': sum(results.mapped('unit_amount'))
            }
            emp.update(res)
