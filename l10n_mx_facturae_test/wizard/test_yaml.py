# -*- encoding: utf-8 -*-
import openerp.tools as tools
import os
from openerp.tools import assertion_report
from openerp.osv import osv, fields
import tempfile
import threading
from openerp import pooler


class test_yaml_facturae(osv.osv_memory):

    _name = 'test.yaml.facturae'

    _columns = {
        'test_commit': fields.boolean('Commit', help='If this field is active, '
                                      'the registers that are created in the '
                                      'test will be saved, else the registers '
                                      'not are saved'),
        'number_invoice': fields.integer('Numbers of invoices',
                                         help='Number of invoices that will be created for test'),
    }

    _defaults = {
        'test_commit': False,
    }

    def test_factuare_run(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        tmp_path = tempfile.gettempdir()
        this = self.browse(cr, uid, ids)[0]
        number_invoices = int(context.get('number_invoice', 0))
        files_names = []
        commit_value = False
        if this.test_commit:
            commit_value = True

        all_paths = tools.config["addons_path"].split(",")
        for my_path in all_paths:
            if os.path.isdir(os.path.join(my_path, u'l10n_mx_cfdi_test', u'test')):
                file_original_yml = open(
                    os.path.join(my_path,
                                 u'l10n_mx_cfdi_test',
                                 u'test',
                                 'test_facturae_pac_all.yml'),
                    "r")
                file_original_yml_read = file_original_yml.read()
                file_original_yml.close()

        for create_invoice in range(0, number_invoices):
            file_name_yml = '%s/account_invoice_cfdi_pac_finkok_%s.yml' % (
                tmp_path, str(create_invoice))
            new_file_modify_yml = file_original_yml_read.replace(
                "journal_ids = acc_jour_obj.search(cr, uid, [], context=context)",
                "journal_ids = acc_jour_obj.search(cr, uid, [('id', '=', ref('l10n_mx_facturae_pac_finkok.l10n_mx_cfdi_pac_finkok_journal_0'))], context=context)").replace(  # noqa
                "list_invoice_demo = ir_model_data.search(cr, uid, [('name', 'ilike', '%'+'facturae_mx'+'%'),('model','=',self._name)], context=context)",  # noqa
                "list_invoice_demo = ir_model_data.search(cr, uid, [('name', 'ilike', '%'+'facturae_mx'+'%'),('model','=',self._name)], limit=1, context=context)")  # noqa
            new_file_modify_yml2 = new_file_modify_yml.replace(
                "for type_test_cancel in ['cancel_from_invoce','cancel_from_attachment_facturae_mx']:", "for type_test_cancel in ['cancel_from_invoce',]:")  # noqa
            new_file_yml = open('%s/account_invoice_cfdi_pac_finkok_%s.yml' %
                                (tmp_path, str(create_invoice)), "w")
            new_file_yml.write(new_file_modify_yml2)
            new_file_yml.close()
            files_names.append([file_name_yml])

        threading_list = []
        for file_name_yml in files_names:
            args = (cr, uid, ids, file_name_yml, commit_value)
            t = threading.Thread(target=self.execute_test_yaml, name=(
                'threading_test_facturae %s' % (create_invoice)), args = args)
            threading_list.append(t)
        for t in threading_list:
            t.setDaemon(False)
            t.start()
        return True

    def execute_test_yaml(self, cr_original, uid, ids, file_name_yml, commit_value):
        assertion_obj = assertion_report.assertion_report()
        cr = None
        fp_test = None
        try:
            cr = False
            # Create a new cursor for close it when is necessary
            cr = pooler.get_db(cr_original.dbname).cursor()
            fp_test = tools.file_open(os.path.join(file_name_yml[0]))
            print threading.currentThread().getName()
            tools.convert_yaml_import(
                cr, 'l10n_mx_cfdi_test', fp_test, 'test', None, 'init', False, assertion_obj)
        finally:
            if cr:
                if commit_value:
                    cr.commit()
                else:
                    cr.rollback()
                    # This is necessary, for clean xml_id_ref var
                    self.pool.get('ir.model.data').clear_caches()
                cr.close()
            if fp_test:
                fp_test.close()
        return True
