#!/usr/bin/python
# -*- encoding: utf-8 -*-
############################################################################### 
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
################# Credits###################################################### 
#    Coded by: Luis Escobar <luis@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################### 
#    This program is free software: you can redistribute it and/or modify       
#    it under the terms of the GNU Affero General Public License as published   
#    by the Free Software Foundation, either version 3 of the License, or       
#    (at your option) any later version.
#                                                                               
#    This program is distributed in the hope that it will be useful,            
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              
#    GNU Affero General Public License for more details.
#                                                                               
#    You should have received a copy of the GNU Affero General Public License   
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      
###############################################################################    

import time
from datetime import datetime                                                                          
import random
import string
                                                                                                       
from openerp.osv import fields, osv                                                                 
from openerp import tools                                                                           
from openerp.tools.translate import _                                                               
import openerp.addons.decimal_precision as dp

class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'
    
    _columns = {
        'vx_contract_code':fields.char('Contract Code', 12, help='Contract Code'), 
            }

    def _contract_code_generator(self, cr, uid, context=None):
        cond = True
        while cond:
            code =  ''.join(random.choice(string.ascii_uppercase + string.digits) for x in
                    range(12))
            code_ids = self.search(cr, uid, [('vx_contract_code','=',code)], context=context)
            if len(code_ids) == 0:
                cond = False
        return code

    def create(self, cr, uid, values, context=None):
        values.update({'vx_contract_code': self._contract_code_generator(cr, uid,
            context=context)})
        return super(account_analytic_account, self).create(cr, uid, values, context=context)

    _defaults = {
        'vx_contract_code': '<<CONTRACT CODE>>',
           }

class account_analytic_accounti_installer(osv.TransientModel):
    _name = 'account.analytic.account.installer'
    _inherit = 'res.config.installer'

    def execute(self, cr, uid, ids, context=None):
        cr.execute("""SELECT vx_contract_code, count(*) cc_count 
                      FROM account_analytic_account
                      GROUP BY vx_contract_code 
                      HAVING count(*) > 1""") 
        contr_obj = self.pool.get('account.analytic.account')
        for row in cr.dictfetchall():
            for idcontract in contr_obj.search(cr, uid,
                    [('vx_contract_code','=',row['vx_contract_code'])], context=context):
                contr_obj.write(cr, uid, [idcontract], {
                  'vx_contract_code': contr_obj._contract_code_generator(cr, uid, context=context),
                }, context=context)

