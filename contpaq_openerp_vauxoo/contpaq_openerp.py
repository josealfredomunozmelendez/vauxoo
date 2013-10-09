# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 OpenERP S.A (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from datetime import datetime

class contpaq_openerp_upload(osv.TransientModel):
    """ Create new issues through the "contact us" form """
    _name = 'contpaq_openerp.contpaq_openerp_upload'
    _description = 'Contact form for the portal'
    _inherit = 'project.issue'

    def _get_domain_contracts(self, cr, uid,context=None):
        partner = self.pool.get('res.users').read(cr, uid, uid, ['partner_id'],
                context)['partner_id']
        cont_ids = self.pool.get('account.analytic.account').search(cr, uid,
                [('date','!=',False), ('vx_contract_code','!=',False)], context=context)
        res = self.pool.get('account.analytic.account').read(cr, uid, cont_ids,
                ['id','vx_contract_code','date_start','date'], context=context)
        result = []
        for list in res:
            name_contract = list['vx_contract_code'] + ' [' + list['date_start']+ ' / ' + \
            list['date']+ ']' 
            result.append((list['id'],name_contract))
        return result 

    _columns = {
        'name':fields.selection(_get_domain_contracts, 'Contract Codes',
             help="""Contract Codes"""), 
        'partner_name':fields.char('Name', 255, help='Partner Name'), 
        'email_from':fields.char('Email', 255, help='Email'), 
        'phone':fields.char('Phone Number', 255, help='Phone Number'), 
        'description':fields.text('Description', help='Description'), 
        'process_ids': fields.many2many('process.process', string='Companies', readonly=True),
        'database_file': fields.binary("Select your file", store=False, filters="*.zip,*.tar.gz,*.tar,*.rar"),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False,
            submenu=False):
        if len(self._get_domain_contracts(cr, uid,context=context)) == 0:
            mod_obj = self.pool.get('ir.model.data') 
            model, view_id = mod_obj.get_object_reference(cr, uid, 'contpaq_openerp_vauxoo',
                'wizard_contact_form_view_nocontract')
        return super(contpaq_openerp_upload, self).fields_view_get(cr, uid, view_id=view_id,
                view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

    def _get_process(self, cr, uid, context=None):
        """
        Fetch companies in order to display them in the wizard view

        @return a list of ids of the companies
        """
        r = self.pool.get('process.process').search(cr, SUPERUSER_ID, [], context=context)
        return r

    def _get_user_name(self, cr, uid, context=None):
        """
        If the user is logged in (i.e. not anonymous), get the user's name to
        pre-fill the partner_name field.
        Same goes for the other _get_user_attr methods.

        @return current user's name if the user isn't "anonymous", None otherwise
        """
        user = self.pool.get('res.users').read(cr, uid, uid, ['login'], context)

        if (user['login'] != 'anonymous'):
            return self.pool.get('res.users').name_get(cr, uid, uid, context)[0][1]
        else:
            return None

    def _get_user_email(self, cr, uid, context=None):
        user = self.pool.get('res.users').read(cr, uid, uid, ['login', 'email'], context)

        if (user['login'] != 'anonymous' and user['email']):
            return user['email']
        else:
            return None

    def _get_user_phone(self, cr, uid, context=None):
        user = self.pool.get('res.users').read(cr, uid, uid, ['login', 'phone'], context)

        if (user['login'] != 'anonymous' and user['phone']):
            return user['phone']
        else:
            return None

    _defaults = {
        'partner_name': _get_user_name,
        'email_from': _get_user_email,
        'phone': _get_user_phone,
        'process_ids': _get_process,
    }

    def create(self, cr, uid, values, context=None):
        sf = ['description','partner_name','email_from','phone','database_file','name']
        r = True
        if set(sf).issubset(values.keys()):
            r = super(contpaq_openerp_upload,self).create(cr,SUPERUSER_ID,values,context=context)
        else:
            raise osv.except_osv(('Error'), ("""No Tiene permitido esta operacion"""))
        return r

    def submit(self, cr, uid, ids, context=None):
        """ When the form is submitted, redirect the user to a "Thanks" message """
        wz_obj = self.read(cr, uid, ids, [], context=context)
        cont_id = int(wz_obj[0]['name'])
        descr = wz_obj[0]['description']
        partner_id = wz_obj[0]['partner_id']
        contract = self.pool.get('account.analytic.account').read(cr, uid, [cont_id],
                ['vx_contract_code','date'], context=context)
        code = contract[0]['vx_contract_code'] 
        venc = contract[0]['date']
        proj_id = self.pool.get('project.project').search(cr, SUPERUSER_ID,
                [('analytic_account_id','=',cont_id)], context=context)
        issue = {
            'name': "Mensaje desde el Contrato " + code, 
            'project_id': proj_id[0],
            'description': descr, 
        }
        now = datetime.now().strftime("%Y-%m-%d")
        if wz_obj[0]['database_file']:
            if now > venc:
                return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': self._name,
                    'res_id': ids[0],
                    'view_id': self.pool.get('ir.model.data').get_object_reference(cr, uid,
                        'contpaq_openerp_vauxoo', 'wizard_contact_form_view_venc')[1],
                    'target': 'inline',
                }
            issue_id = self.pool.get('project.issue').create(cr, SUPERUSER_ID, issue,
                    context=context)
            att_dict = {'res_model': 'project.issue',                                                                
                   'res_id': issue_id,
                   'name':  code + '-database',
                   'type': 'binary',
                   'user_id': uid,
                   'datas': wz_obj[0]['database_file'],
                   'partner_id': partner_id }
            att_id = self.pool.get('ir.attachment').create(cr, SUPERUSER_ID,att_dict,
                    context=context)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': self._name,
            'res_id': ids[0],
            'view_id': self.pool.get('ir.model.data').get_object_reference(cr, uid, 'contpaq_openerp_vauxoo', 'wizard_contact_form_view_thanks')[1],
            'target': 'inline',
        }

    def _needaction_domain_get(self, cr, uid, context=None):
        """
        This model doesn't need the needactions mechanism inherited from
        crm_lead, so simply override the method to return an empty domain
        and, therefore, 0 needactions.
        """
        return False
