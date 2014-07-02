# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
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
#
import openerp.tools as tools
import os
from openerp.tools import assertion_report
import sys
import base64
from openerp.osv import osv, fields
import tempfile
import shutil
import threading
from openerp import pooler
import time


class test_yaml_facturae(osv.osv_memory):

    _name = 'test.yaml.facturae'

    _columns = {
        'test_commit': fields.boolean('Commit'),
        'number_invoice': fields.integer('Numbers of invoice'),
    }

    _defaults = {
        'test_commit': False,
    }
    
    
    def test_factuare_run(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        tmp_path = tempfile.gettempdir()
        assertion_obj = assertion_report.assertion_report()
        this = self.browse(cr, uid, ids)[0]
        number_invoices = int(context.get('number_invoice'))
        files_names = []
        commit_value = False
        if this.test_commit:
            commit_value = True

        all_paths = tools.config["addons_path"].split(",")
        for my_path in all_paths:
            if os.path.isdir(os.path.join(my_path, u'l10n_mx_cfdi_test', u'test')):
                file_original_yml = open(
                    os.path.join(my_path, u'l10n_mx_cfdi_test', u'test', 'test_facturae_pac_all.yml'), "r")
                file_original_yml_read = file_original_yml.read()
                file_original_yml.close()

        for create_invoice in range(0, number_invoices):
            file_name_yml = '%s/account_invoice_cfdi_pac_finkok_%s.yml' % (
                tmp_path, str(create_invoice))
            new_file_modify_yml = file_original_yml_read.replace(
                "journal_ids = acc_jour_obj.search(cr, uid, [], context=context)", 
                "journal_ids = acc_jour_obj.search(cr, uid, [('id', '=', ref('l10n_mx_facturae_pac_finkok.l10n_mx_cfdi_pac_finkok_journal_0'))], context=context)")
            new_file_modify_yml2 = new_file_modify_yml.replace(
                "for type_test_cancel in ['cancel_from_invoce','cancel_from_attachment_facturae_mx']:", "for type_test_cancel in ['cancel_from_invoce',]:")
            new_file_yml = open('%s/account_invoice_cfdi_pac_finkok_%s.yml' %
                                (tmp_path, str(create_invoice)), "w")
            new_file_yml.write(new_file_modify_yml2)
            new_file_yml.close()
            files_names.append([file_name_yml])
        
        threading_list = []
        for file_name_yml in files_names:
            args = (cr, uid, ids, file_name_yml,commit_value)
            t = threading.Thread(target=self.execute_test_yaml, name=(
                'threading_test_facturae %s' % (create_invoice) ), args = args)
            threading_list.append( t )
        for t in threading_list:
            #~ t.daemon = False
            t.setDaemon(False)
            t.start()
        return True

    def execute_test_yaml(self, cr_original, uid, ids, file_name_yml,commit_value):
        assertion_obj = assertion_report.assertion_report()
        cr = None
        fp_test = None
        #process_name = os.path.splitext( os.path.basename( file_name_xml ) )[0]#unique file name then unique process name
        try:
            cr = False
            cr = pooler.get_db(cr_original.dbname).cursor()#Create a new cursor for close it when is necessary
            fp_test = tools.file_open(os.path.join(file_name_yml[0]))
            print threading.currentThread().getName()
            tools.convert_yaml_import(
                cr, 'l10n_mx_cfdi_test', fp_test, 'test' , None, 'init' , False, assertion_obj)
        finally:
            if cr:
                if commit_value:
                    cr.commit()
                else:
                    cr.rollback()
                    self.pool.get('ir.model.data').clear_caches()#This is necessary, for clean xml_id_ref var
                cr.close()
            if fp_test:
                fp_test.close()
        return True
    
    '''
    def test_factuare_run(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        tmp_path = tempfile.gettempdir()
        assertion_obj = assertion_report.assertion_report()
        this = self.browse(cr, uid, ids)[0]
        number_invoices = int(context.get('number_invoice'))
        files_names = []
        commit_value = False
        if this.test_commit:
            commit_value = True

        #~ TODO: Remplazar todos los xml_ids
        all_paths = tools.config["addons_path"].split(",")
        for my_path in all_paths:
            if os.path.isdir(os.path.join(my_path, u'l10n_mx_facturae_pac_sf', u'demo')):
                file_original_xml = open(
                    os.path.join(my_path, u'l10n_mx_facturae_pac_sf', u'demo', 'account_invoice_cfdi_pac_sf_demo.xml'), "r")
                file_original_xml_read = file_original_xml.read()
                file_original_xml.close()
            if os.path.isdir(os.path.join(my_path, u'l10n_mx_facturae_pac_sf', u'test')):
                file_original_yml = open(
                    os.path.join(my_path, u'l10n_mx_facturae_pac_sf', u'test', 'account_invoice_cfdi_pac_sf.yml'), "r")
                file_original_yml_read = file_original_yml.read()
                file_original_yml.close()

        for create_invoice in range(0, number_invoices):
            file_name_xml = '%s/account_invoice_cfdi_pac_sf_demo_%s.xml' % (
                tmp_path, str(create_invoice))
            new_file_xml = open('%s/account_invoice_cfdi_pac_sf_demo_%s.xml' %
                                (tmp_path, str(create_invoice)), "w")
            new_file_modify_xml = file_original_xml_read.replace(
                'account_invoice_cfdi_pac_sf0', 'account_invoice_cfdi_pac_sf0_%s' % (str(create_invoice)))
            new_file_modify_xml2 = new_file_modify_xml.replace(
                '900.0', '%s' % (str(901 + create_invoice)))
            new_file_xml.write(new_file_modify_xml2)
            new_file_xml.close()

            file_name_yml = '%s/account_invoice_cfdi_pac_sf_%s.yml' % (
                tmp_path, str(create_invoice))
            new_file_modify_yml = file_original_yml_read.replace(
                'account_invoice_cfdi_pac_sf0', 'account_invoice_cfdi_pac_sf0_%s' % (str(create_invoice)))
            new_file_yml = open('%s/account_invoice_cfdi_pac_sf_%s.yml' %
                                (tmp_path, str(create_invoice)), "w")
            new_file_yml.write(new_file_modify_yml)
            new_file_yml.close()

            files_names.append([file_name_xml, file_name_yml])
        
        threading_list = []
        for file_name_xml, file_name_yml in files_names:
            args = (cr, uid, ids, file_name_xml, file_name_yml,commit_value)
            t = threading.Thread(target=self.execute_test_yaml, name=(
                'threading_test_facturae: ' + file_name_yml), args = args)
            threading_list.append( t )
        for t in threading_list:
            #~ t.daemon = False
            t.setDaemon(True)
            t.start()
        return True

    def execute_test_yaml(self, cr_original, uid, ids, file_name_xml, file_name_yml,commit_value):
        print threading.currentThread().getName()
        assertion_obj = assertion_report.assertion_report()
        cr = None
        fp_data = None
        fp_test = None
        #process_name = os.path.splitext( os.path.basename( file_name_xml ) )[0]#unique file name then unique process name
        try:
            cr = False
            cr = pooler.get_db(cr_original.dbname).cursor()#Create a new cursor for close it when is necessary
            fp_data = tools.file_open(os.path.join(file_name_xml))
            fp_test = tools.file_open(os.path.join(file_name_yml))
            tools.convert_xml_import(
                cr, 'l10n_mx_facturae_pac_sf', fp_data, None, 'init', False, assertion_obj)
            tools.convert_yaml_import(
                cr, 'l10n_mx_facturae_pac_sf', fp_test, 'test' , None, 'init' , False, assertion_obj)
        finally:
            if cr:
                cr.rollback()
                self.pool.get('ir.model.data').clear_caches()#This is necessary, for clean xml_id_ref var
                cr.close()
            if fp_data:
                fp_data.close()
            if fp_test:
                fp_test.close()
        return True
    '''
