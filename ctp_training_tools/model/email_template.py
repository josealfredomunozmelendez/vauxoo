# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _


class email_template(osv.Model):
    _inherit = "email.template"

    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        action_obj = self.pool.get('ir.actions.act_window')
        data_obj = self.pool.get('ir.model.data')
        for template in self.browse(cr, uid, ids, context=context):
            src_obj = template.model_id.model
            model_data_id = data_obj._get_id(
                cr, uid, 'mail', 'email_compose_message_wizard_form')
            res_id = data_obj.browse(
                cr, uid, model_data_id, context=context).res_id
            button_name = _('Send Mail (%s)') % template.name
            vals['ref_ir_act_window'] = action_obj.create(cr, uid, {
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'src_model': src_obj,
                'view_type': 'form',
                'context': "{'default_composition_mode': 'mass_mail', 'default_template_id' : %d, 'default_use_template': True}" % (template.id),
                'view_mode': 'form,tree',
                'view_id': res_id,
                'target': 'new',
                'auto_refresh': 1
            }, context)
            vals['ref_ir_value'] = self.pool.get('ir.values').create(cr, uid, {
                'name': button_name,
                'model': src_obj,
                'key2': 'client_action_multi',
                'value': "ir.actions.act_window," + str(vals['ref_ir_act_window']),
            }, context)
        self.write(cr, uid, ids, {
            'ref_ir_act_window': vals.get('ref_ir_act_window', False),
            'ref_ir_value': vals.get('ref_ir_value', False),
        }, context)
        return True
