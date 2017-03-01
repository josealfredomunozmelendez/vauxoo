# coding: utf-8
from odoo import models, fields, api


class Project(models.Model):

    _inherit = "project.project"

    label_acronymous = fields.Char(
        copy="False", default="HU", size=4,
        help="Acronymous to show as prefix in the display name for the tasks"
             " without parent Tasks")
    label_acronymous_subtasks = fields.Char(
        copy="False", default="CA", size=4,
        help="Acronymous to show as prefix in the display name for the tasks"
             " with parent Tasks")


class ProjectTask(models.Model):

    _inherit = "project.task"

    ticket_id = fields.Many2one(
        "helpdesk.ticket", copy="False")
    display_name = fields.Char(
        "Name", compute="_compute_display_name", store=True, index=True)
    product_id = fields.Many2one(
        related="sale_line_id.product_id", readonly=True)

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
