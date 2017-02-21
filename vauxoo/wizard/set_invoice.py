# coding: utf-8
from odoo import models, fields, api


class SetInvoice(models.TransientModel):

    _name = 'set.invoice'

    @api.model
    def default_get(self, fields_list):
        htr = False
        res = super(SetInvoice, self).default_get(fields_list)
        context = self.env._context
        # TODO take care here danger review if the context is properly working
        ids = context.get('active_ids', False)
        model = context.get('active_model', False)
        report_id = context.get('ts_report_id', False)
        if report_id:
            htr_obj = self.env['hr.timesheet.reports.base']
            htr = htr_obj.browse(report_id)
        obj = self.env[model]
        brws = obj.browse(ids)
        # TODO take care here with this ids (int or recordset?)
        total_h = sum(
            [b.invoiceables_hours for b in brws if b.invoiceables_hours])
        res.update({
            'total_timesheet': total_h,
            'total_money': htr and total_h * htr.product_id.list_price or 0.00,
            'currency_id': htr and htr.currency_id.id,
        })

        return res

    total_timesheet = fields.Float(
        'Total Timesheet to set',
        help="This will be the quantity to be setted to this invoice be sure "
        "quantities are consistent")

    total_money = fields.Float(
        'Total Timesheet in Money',
        help="Total in money with the currency and product of the report"
        " which you comes from")

    currency_id = fields.Many2one(
        'product.product', 'Currency', help='Currency on report')
