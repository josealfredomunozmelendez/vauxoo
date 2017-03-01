# coding: utf-8
from odoo import models, fields, api


class ProjectTask(models.Model):

    _inherit = "project.task"

    ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Helpdesk Ticket",
        copy="False")

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


class ProjectProject(models.Model):

    _inherit = "project.project"

    use_subtasks = fields.Boolean(
        string="Sub-Tasks",
        copy="False",
        help="Check this box to manage internal sub-activities through this"
        " project")

    label_subtasks = fields.Char(
        string="Use Sub Tasks as",
        default="Sub-Tasks",
        help="Gives label to sub-tasks on project's kanban view")
