# coding: utf-8
from __future__ import division
from datetime import datetime, timedelta, date

from odoo import fields, models, api, _


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


class HrDepartment(models.Model):

    _inherit = "hr.department"

    is_cost = fields.Integer(
        compute='_compute_total_salary',
        help="Number of employees who are Cost")
    generate_income = fields.Integer(
        compute='_compute_total_salary',
        help="Number of employees who Generate Income")
    salary_on_job = fields.Float(
        track_visibility='onchange',
        compute='_compute_total_salary',
        inverse='_inverse_total_salary',
        help="Salary conceptual on job")
    total_salary = fields.Float(
        track_visibility='onchange',
        compute='_compute_total_salary',
        inverse='_inverse_total_salary',
        help="How much it is costing after payroll comes in, USD")
    theoretical_timesheet = fields.Float(
        default=100.00,
        track_visibility='onchange',
        compute='_compute_total_salary',
        help="Manually computed value to take know how is the effective of "
             "this person in terms of timesheet use 120 for a great resource "
             "10 for a newbie")
    perceived_salary = fields.Float(
        track_visibility='onchange',
        compute='_compute_total_salary',
        inverse='_inverse_total_salary',
        help="How much this person is receiving monthly, USD")
    theoretical_cost = fields.Float(
        compute="_compute_total_salary",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    current_cost = fields.Float(
        compute="_compute_total_salary",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    theoretical_cost_avg = fields.Float(
        compute="_compute_total_salary",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    current_cost_avg = fields.Float(
        compute="_compute_total_salary",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    hours_invoice = fields.Float(
        compute='_compute_total_salary',
        help="How many hours this person is being reporting")
    hours_informed = fields.Float(
        compute='_compute_total_salary',
        help="How many hours this person is having billable")

    @api.depends()
    def _compute_total_salary(self):
        for dep in self:
            salary_on_job = 0.0
            total_salary = 0.0
            perceived_salary = 0.0
            theoretical_cost = 0.0
            current_cost = 0.0
            hours_invoice = 0.0
            hours_informed = 0.0
            theoretical_timesheet = 0
            is_cost = 0
            generate_income = 0
            for emp in dep.member_ids:
                salary_on_job += emp.salary_on_job
                total_salary += emp.total_salary
                perceived_salary += emp.perceived_salary
                theoretical_cost += emp.theoretical_cost
                current_cost += emp.current_cost
                hours_invoice += emp.hours_invoice
                hours_informed += emp.hours_informed
                theoretical_timesheet += emp.theoretical_timesheet
                is_cost += int(emp.is_cost)
                generate_income += int(emp.generate_income)
            qty = dep.total_employee
            dep.update(dict(
                salary_on_job=salary_on_job,
                total_salary=total_salary,
                perceived_salary=perceived_salary,
                theoretical_cost=theoretical_cost,
                current_cost=current_cost,
                theoretical_cost_avg=theoretical_cost / qty if qty else 0.0,
                current_cost_avg=current_cost / qty if qty else 0.0,
                hours_invoice=hours_invoice,
                hours_informed=hours_informed,
                theoretical_timesheet=theoretical_timesheet,
                is_cost=is_cost,
                generate_income=generate_income,
            ))


class HrJob(models.Model):

    _inherit = "hr.job"

    wage = fields.Float(
        track_visibility='onchange',
        help="Conceptual wage this job should win (to planning purposes)")
    is_cost = fields.Integer(
        compute='_compute_total_salary',
        help="Number of employees who are Cost")
    generate_income = fields.Integer(
        compute='_compute_total_salary',
        help="Number of employees who Generate Income")
    employee_qty = fields.Integer(
        compute='_compute_total_salary',
        help="Number of employees in Job Position")
    salary_on_job = fields.Float(
        track_visibility='onchange',
        compute='_compute_total_salary',
        inverse='_inverse_total_salary',
        help="Salary conceptual on job")
    total_salary = fields.Float(
        track_visibility='onchange',
        compute='_compute_total_salary',
        inverse='_inverse_total_salary',
        help="How much it is costing after payroll comes in, USD")
    theoretical_timesheet = fields.Float(
        default=100.00,
        track_visibility='onchange',
        compute='_compute_total_salary',
        help="Manually computed value to take know how is the effective of "
             "this person in terms of timesheet use 120 for a great resource "
             "10 for a newbie")
    perceived_salary = fields.Float(
        track_visibility='onchange',
        compute='_compute_total_salary',
        inverse='_inverse_total_salary',
        help="How much this person is receiving monthly, USD")
    theoretical_cost = fields.Float(
        compute="_compute_total_salary",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    current_cost = fields.Float(
        compute="_compute_total_salary",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    theoretical_cost_avg = fields.Float(
        compute="_compute_total_salary",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    current_cost_avg = fields.Float(
        compute="_compute_total_salary",
        track_visibility='onchange',
        help="Computed cost from the total list of employees")
    hours_invoice = fields.Float(
        compute='_compute_total_salary',
        help="How many hours this person is being reporting")
    hours_informed = fields.Float(
        compute='_compute_total_salary',
        help="How many hours this person is having billable")

    @api.depends()
    def _compute_total_salary(self):
        for job in self:
            salary_on_job = 0.0
            total_salary = 0.0
            perceived_salary = 0.0
            theoretical_cost = 0.0
            current_cost = 0.0
            hours_invoice = 0.0
            hours_informed = 0.0
            theoretical_timesheet = 0
            is_cost = 0
            generate_income = 0
            for emp in job.employee_ids:
                salary_on_job += emp.salary_on_job
                total_salary += emp.total_salary
                perceived_salary += emp.perceived_salary
                theoretical_cost += emp.theoretical_cost
                current_cost += emp.current_cost
                hours_invoice += emp.hours_invoice
                hours_informed += emp.hours_informed
                theoretical_timesheet += emp.theoretical_timesheet
                is_cost += int(emp.is_cost)
                generate_income += int(emp.generate_income)
            qty = len(job.employee_ids)
            job.update(dict(
                salary_on_job=salary_on_job,
                total_salary=total_salary,
                perceived_salary=perceived_salary,
                theoretical_cost=theoretical_cost,
                current_cost=current_cost,
                theoretical_cost_avg=theoretical_cost / qty if qty else 0.0,
                current_cost_avg=current_cost / qty if qty else 0.0,
                hours_invoice=hours_invoice,
                hours_informed=hours_informed,
                theoretical_timesheet=theoretical_timesheet,
                is_cost=is_cost,
                generate_income=generate_income,
                employee_qty=qty,
            ))


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
    is_cost_select = fields.Selection(
        compute='_compute_employee_select',
        string='Selectable Field for is_cost',
        selection=[('False', 'False'), ('True', 'True')],
        help='A field for reporting purpose'
    )
    generate_income_select = fields.Selection(
        compute='_compute_employee_select',
        string='Selectable Field for generate_income',
        selection=[('False', 'False'), ('True', 'True')],
        help='A field for reporting purpose'
    )
    hours_invoice = fields.Float(
        compute='_compute_timesheet_average',
        help="How many hours this person is being reporting")
    hours_informed = fields.Float(
        compute='_compute_timesheet_average',
        help="How many hours this person is having billable")
    employee_badge_ids = fields.One2many(
        'gamification.badge',
        string='Employee Badge',
        compute='_compute_employee_badges',
        help='Field to hold all employee badges'
    )
    employee_task_ids = fields.One2many(
        'project.task',
        string='Employee Tasks',
        compute='_compute_employee_tasks',
        help='Field to hold all employee tasks'
    )
    task_count = fields.Integer(
        compute='_compute_employee_tasks',
        help='Number of Tasks per employee'
    )
    task_done = fields.Integer(
        compute='_compute_employee_tasks',
        help='Number of Tasks Done per employee'
    )
    task_todo = fields.Integer(
        compute='_compute_employee_tasks',
        help='Number of Tasks ToDo per employee'
    )
    task_perc = fields.Integer(
        compute='_compute_employee_tasks',
        help='Percentage of Done Tasks per employee'
    )

    @api.depends()
    def _compute_employee_select(self):
        for emp in self:
            emp.is_cost_select = 'True' if emp.is_cost else 'False'
            emp.generate_income_select = \
                'True' if emp.generate_income else 'False'

    @api.depends()
    def _compute_employee_tasks(self):
        task_obj = self.env['project.task']
        for employee in self:
            if not employee.user_id:
                continue
            task_ids = task_obj.search(
                [('user_id', '=', employee.user_id.id),
                 ('stage_id', 'not in', ('Cancelled',)),
                 ])
            employee.employee_task_ids = task_ids
            task_count = len(task_ids)
            done = len(task_ids.filtered(lambda t: t.stage_id.name == 'Done'))
            perc = 100 * done / task_count if task_count else 0.0
            employee.task_count = task_count
            employee.task_done = done
            employee.task_todo = task_count - done
            employee.task_perc = perc

    @api.depends('direct_badge_ids', 'user_id.badge_ids.employee_id')
    def _compute_employee_badges(self):
        super(HrEmployee, self)._compute_employee_badges()
        res = dict.fromkeys(self.ids, self.env['gamification.badge'])
        for employee in self:
            for badge in employee.badge_ids:
                res[employee.id] |= badge.badge_id
            employee.employee_badge_ids = res[employee.id]

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
                'total_salary': emp.total_salary,
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
        theoretical = sum(employees_cost.mapped('salary_on_job'))
        salaries = sum(employees_cost.mapped('total_salary'))
        hours = sum(employees_generate.mapped('theoretical_timesheet'))
        hours_real = sum(employees_generate.mapped('hours_invoice'))
        hours_billable = sum(employees_generate.mapped('hours_invoice'))
        budgeted = -sum(budgets.mapped('crossovered_budget_line').filtered(
            lambda line: line.planned_amount < 0.0).mapped('amount_usd'))
        cost = float((theoretical + budgeted) / hours) if hours else 0.00
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
