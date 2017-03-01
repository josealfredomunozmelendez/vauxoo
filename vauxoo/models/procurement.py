# coding: utf-8
from odoo import models, _


class ProcurementOrder(models.Model):

    _inherit = "procurement.order"

    def _create_service_task(self):
        """ All task created form sale order are marked ad blocked task until
        the sale order has been paid.
        """
        task = super(ProcurementOrder, self)._create_service_task()
        new_name = task.sale_line_id.name.split('\n')[0]
        task.write(dict(
            name=new_name,
            kanban_state="blocked",
            user_id=task.project_id.user_id.id,
            color=6))
        # TODO maybe this default color for the user stories can be configured
        # somewhere as a system parameter
        task.message_post(body=_(
            "This task will be blocked until the sale order has been paid"))
        return task
