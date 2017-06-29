# coding: utf-8
from odoo import models, fields, api


class Project(models.Model):

    _inherit = "project.project"

    label_acronymous = fields.Char(
        copy="False", default="HU", size=4,
        help="Acronymous to show as prefix in the display name for the tasks"
             " without parent Tasks")
    label_subtasks = fields.Char(
        copy="False", default="Sub Tasks",
        help="Acronymous to show as prefix in the display name for the tasks"
             " with parent Tasks")
    label_acronymous_subtasks = fields.Char(
        copy="False", default="CA", size=4,
        help="Acronymous to show as prefix in the display name for the tasks"
             " with parent Tasks")

    def _compute_task_count(self):
        """ Modify the task count to only take into account the parent tasks
        that are not orphan tasks.
        """
        for project in self:
            project.task_count = len(self.env['project.task'].search([
                ('id', 'in', project.task_ids.mapped('id')),
                ('parent_id', '=', False),
            ]))


class ProjectTask(models.Model):

    _inherit = "project.task"

    ticket_id = fields.Many2one(
        "helpdesk.ticket", copy="False")
    display_name = fields.Char(
        "Name", compute="_compute_display_name", store=True, index=True)
    product_id = fields.Many2one(
        related="sale_line_id.product_id", readonly=True)
    label_subtasks = fields.Char(
        related="project_id.label_subtasks", readonly=True)
    # User Story Specific Information
    description = fields.Html(track_visibility="onchange")
    planned_hours = fields.Float(
        string='Initially Planned Hours',
        help='Estimated time to do the task, usually set by the project '
             'manager when the task is in draft state.',
        track_visibility="onchange")
    owner_id = fields.Many2one(
        'res.users',
        help="User Story's Owner, generally the person which asked to develop "
             "this feature on customer side",
        track_visibility='always')
    approving_id = fields.Many2one(
        'res.users',
        help="User which says this User Story must/can be done")
    billable_hours = fields.Float()
    difficulty_id = fields.Many2one(
        'project.task.estimation',
        help="How difficult/clear is this ")
    budget = fields.Float(help="Estimated budget in dollars")
    currency_id = fields.Many2one(
        'res.currency',
        help="Currency which the budget was planned on (default usd)",
        default=lambda self: self.env.ref('base.USD'))
    # Grouping Information for Mapping.
    group_id = fields.Many2one('project.task')
    list_id = fields.Many2one('project.task')
    layer_id = fields.Many2one('project.task')
    gap = fields.Text(track_visibility="onchange")
    asumption = fields.Text(track_visibility="onchange")
    implementation = fields.Text(track_visibility="onchange")

    @api.model
    def default_get(self, field_list):
        res = super(ProjectTask, self).default_get(field_list)
        res.update({'name': ''})
        return res

    @api.depends('parent_id', 'sale_line_id', 'name')
    def _compute_display_name(self):
        # all user don't have access to sale orders
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        for task in self.sudo():
            if not task.name:
                task.display_name = ''
                continue
            name = task.name
            order = False
            if task.sale_line_id:
                order = task.sale_line_id.order_id.name
            if not task.parent_id:
                prefix = task.project_id.label_acronymous or ''
                story = prefix + (str(task.id) or '...')
                criteria = ''
            else:
                prefix = task.project_id.label_acronymous or ''
                story = prefix + (str(task.parent_id.id))
                prefix = task.project_id.label_acronymous_subtasks or ''
                criteria = prefix + (str(task.id) or '...')
            elements = [order, story, criteria, name]
            elements = [e for e in elements if e]
            task.display_name = ":".join(elements)

    @api.multi
    def open_subtasks(self):
        self.ensure_one()
        action = self.env.ref('project.project_task_action_from_partner')
        [action_dict] = action.read([])
        ctx = dict(self._context)
        ctx.update({
            'search_default_parent_id': self.id,
            'default_parent_id': self.id})
        action_dict['context'] = ctx
        action_dict['domain'] = [("parent_id", "=", self.id)]
        return action_dict


class UserStoryDifficulty(models.Model):
    _name = 'project.task.estimation'
    _order = "points asc"
    _description = '''Based on scrum cards values for estimation but used for
user stories estimations'''

    name = fields.Char(required=True, translate=True)
    points = fields.Float(
        required=True,
        help="Just to give another value to criterias and User Stories."
             " With it you can set an order and a value in terms of"
             " effort")
    estimated = fields.Float(
        required=True,
        help="How many hour do you think it can take?")
    help = fields.Text(
        help="Explain what kind of User Stories can be on this level,"
             " tell your experience give examples and so on.")

    @api.multi
    def name_get(self):
        def _name_get(data_name):
            name = data_name.get('name', '')
            return data_name['id'], name
        res = []
        for difficulty in self:
            name = '[%s] %s points, represent %s hours' % (
                difficulty.name,
                difficulty.points,
                difficulty.estimated)
            my_dict = {'id': difficulty.id, 'name': name, }
            res.append(_name_get(my_dict))
        return res
