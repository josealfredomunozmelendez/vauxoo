# !/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import json
import csv
import pprint
import logging
from collections import defaultdict
import psycopg2
import odoorpc
import click
import click_log
import py
from odoo_csv_tools.import_threaded import import_data
from odoo_csv_tools.export_threaded import export_data

__version__ = '1.0.1'

logging.addLevelName(
    logging.ERROR,
    "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(
    logging.INFO,
    "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
logging.addLevelName(
    logging.WARNING,
    "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(
    logging.DEBUG,
    "\033[1;34m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
logging.addLevelName(
    logging.CRITICAL,
    "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))

_logger = logging.getLogger('vxmigration')
_logger.setLevel(logging.DEBUG)
CH_VAR = logging.StreamHandler()
CH_VAR.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
CH_VAR.setFormatter(FORMATTER)
_logger.addHandler(CH_VAR)


class Migration(object):

    def __init__(
            self, legacy, new_instance, cursor, max_connection, batch_size):
        self.legacy = legacy
        self.new_instance = new_instance
        self.cr = cursor
        self.group_size = 100
        self.dummy_ir_models = []
        self.max_connection = max_connection
        self.batch_size = batch_size
        self.new_instance.env.context.update(
            {'tracking_disable': True,
             'write_metadata': True})

        header = ['model', 'record', 'id', 'name', 'message']
        with open('migration_errors.csv', 'w', newline='') as csvfile:
            wr = csv.writer(csvfile)
            wr.writerow(header)

    def load(self, model, load_fields, load_data_group):
        # loaded_data = self.new_instance.execute(
        #     model, 'load', load_fields, load_data_group)
        messages, fails, ids = import_data(
            registry=self.new_instance, model=model,
            header=load_fields, data=load_data_group,
            max_connection=self.max_connection, batch_size=self.batch_size)

        if not ids:
            self.write_errors(model, load_fields, load_data_group)
        return {'failed': fails, 'messages': messages, 'ids': ids}

    def export(self, model, ids, export_fields):
        # export_data = self.legacy.execute(
        #     model, 'export_data', ids, export_fields)
        # return export_data

        ids = export_data(
            registry=self.legacy, model=model, ids=ids, header=export_fields,
            max_connection=self.max_connection, batch_size=self.batch_size)
        return {'datas': ids}

    def test(self):
        for instance in [self.legacy, self.new_instance]:
            user = instance.env.user
            _logger.debug("- User " + user.name + " (Company " +
                          user.company_id.name + ")")

    def ref_inv(self, res_id, model):
        """ Inverse method of orm.ref. will receive an id and a model and will
        return the xml_id of the record """
        xml_id = False
        record = self.new_instance.execute(
            'ir.model.data', 'search',
            [('res_id', '=', res_id), ('model', '=', model)])
        if record:
            xml_id = self.new_instance.execute(
                'ir.model.data', 'read', record[0]).get('complete_name', False)
        return xml_id

    def chunks(self, values):
        """Split a list into a n sublist, where n is the group_size configured
        in the class.
        """
        number = self.group_size
        groups = [values[item:item + number]
                  for item in range(0, len(values), number)]
        group_number = len(groups)
        _logger.info("%s groups of %s" % (group_number, number))
        return groups, group_number

    def get_record_name(self, module, xml_id):
        """ return the record name in new instance of the module.xml_id given
        """
        model, record_id = self.new_instance.execute(
            'ir.model.data', 'get_object_reference', module, xml_id)
        record_name = self.new_instance.execute(
            model, 'read', record_id, ['name'])[0].get('name')
        return record_name

    def list2dict(self, fields, values):
        data = dict()
        for (index, _item) in enumerate(fields):
            data.update({fields[index]: values[index]})
        return data

    def res_lang_mapping(self, lang):
        """ Now we have only one Spanish, make the mapping to the records
        that have Spanish.
        """
        return r'Spanish / Español' if lang in ['es_MX', 'es_VE', 'es_PA'] \
            else lang

    def mapping_groups(self, groups):
        """ Remove deprecated groups from the res users groups to import list
        """
        deprecated_to_remove = set([
            'account.group_supplier_inv_check_total',
            'account_analytic_analysis.group_template_required',
            'account_financial_report.group_afreport',
            'account_financial_report.group_afreport_user',
            'account_group_auditory.group_account_user_audit',
            'base.group_document_user',
            'base.group_hr_attendance',
            'base.group_hr_manager',
            'base.group_hr_user',
            'base.group_mono_salesteams',
            'base.group_multi_salesteams',
            'base.group_sale_manager',
            'base.group_sale_salesman',
            'base.group_sale_salesman_all_leads',
            'base.group_survey_manager',
            'base.group_survey_user',
            'base.group_website_designer',
            'base.group_website_publisher',
            'city.group_res_country_state_city_manager',
            'crm.group_fund_raising',
            'crm.group_scheduled_calls',
            'ctp_training_tools.certificate_manager',
            'expired_task_information.group_config_task_expiry',
            'gamification.group_goal_manager',
            'ifrs_report.group_ifrsreport',
            'ifrs_report.group_ifrsreport_user',
            'invoice_datetime.group_invoice_hide_datetime',
            'l10n_facturae_groups_multipac_vauxoo'
            '.group_l10n_mx_facturae_multipac_manager',
            'l10n_facturae_groups_multipac_vauxoo'
            '.group_l10n_mx_facturae_multipac_user',
            'l10n_mx_facturae_22_regimen_fiscal.group_regimen_fiscal_manager',
            'l10n_mx_facturae_22_regimen_fiscal.group_regimen_fiscal_user',
            'l10n_mx_facturae_base.group_l10n_mx_facturae_print_inv_default',
            'l10n_mx_facturae_group_show_wizards'
            '.res_group_facturae_show_default_wizards',
            'l10n_mx_facturae_groups.group_l10n_mx_facturae_manager',
            'l10n_mx_facturae_groups.group_l10n_mx_facturae_user',
            'l10n_mx_facturae_groups.group_l10n_mx_xml_cancel',
            'l10n_mx_facturae_groups.group_l10n_mx_xml_regenerate_xml',
            'l10n_mx_ir_attachment_facturae.group_l10n_mx_itfm_force_signed',
            'l10n_mx_params_pac.res_group_pacs',
            'lunch.group_lunch_manager',
            'lunch.group_lunch_user',
            'mail_add_followers_multirecord'
            '.group_mail_add_followers_multirecord',
            'marketing.group_marketing_manager',
            'marketing.group_marketing_user',
            'mass_mailing.group_mass_mailing_campaign',
            'note.group_note_fancy',
            'portal_sale.group_payment_options',
            'product.group_mrp_properties',
            'product.group_purchase_pricelist',
            'product.group_uos',
            'project.group_delegate_task',
            'project.group_tasks_work_on_tasks',
            'project_followers_rule.group_followers_project',
            'project_issue_management.project_auditor',
            'purchase.group_advance_bidding',
            'sale.group_invoice_so_lines',
            'sale.group_mrp_properties',
            'sale_order_copy_line.group_sale_order_line_copy',
            'sale_stock.group_invoice_deli_orders',
            'set_group_by_department.res_group_vx_administrative_team',
            'set_group_by_department.res_group_vx_manager_team',
            'set_group_by_department.res_group_vx_technical_team',
            'share.group_share_user',
            'share.group_shared',
            'sprint_kanban.group_sprint_kanban_manager',
            'sprint_kanban.group_sprint_kanban_user',
            'stock.group_locations',
            'user_story.group_management_reports',
            'user_story.group_user_story_manager',
            'user_story.group_user_story_user',
            'website_mail.group_comment'
        ])

        if not groups:
            return groups

        groups = set(groups.split(','))
        groups = groups - deprecated_to_remove
        return ','.join(groups)

    def res_company_mapping(self):
        """ Will create the xml_id for the existent companies
        """
        _logger.info("Mapping Companies")

        # Search if the company mapping has not been created before.
        model = 'res.company'

        # Dummy external ids for avoid company mapping.
        fields = ['model', 'res_id', 'id', 'module', 'name']
        values = [
            [model, 3, 'dummy_res_company_ve',
             '__export__', 'res_company_5'],
            # TODO Do not import this companies by now
            # id 3, Vauxoo CA, Venezuela
            # id 4, Vauxoo SA, Peru
            # [model, 1, 'dummy_res_company_mx', '__export__',
            # 'res_company_3'],
            # [model, 1, 'dummy_res_company_con', '__export__',
            # 'res_company_4'],
        ]
        dummys = self.load(
            'ir.model.data', fields, values)

        self.dummy_ir_models.extend(dummys.get('ids', []))

    def res_country_state_mapping(self):
        _logger.info("Mapping Federal States")
        model = 'res.country.state'

        # Found out the states to imported
        legacy_ids = self.legacy.execute('res.country.state', 'search', [
            # Next states are repated and need to be mapped in order to work
            # with saas-14
            ('id', 'not in', ['118', '87', '100']),
        ])
        export_fields = ['code', 'id', 'name', 'country_id/id',
                         'country_id/code', 'country_id/.id']
        legacy_data = self.export(
            'res.country.state', legacy_ids, export_fields).get('datas', [])

        to_import = []
        to_mapping = []
        for item in legacy_data:
            new_id = self.new_instance.execute(
                'res.country.state', 'search', [
                    ('code', '=', item[0].upper()),
                    ('country_id', '=', item[4])])
            if new_id:
                module, name = item[1].split('.')
                xml = self.new_instance.execute(
                    'ir.model.data', 'search', [
                        ('module', '=', module), ('name', '=', name)])
                if not xml:
                    to_mapping.append([new_id[0], module, name])
            else:
                to_import.append(item[:-2])

        # Importing non Mexico states
        load_fields = ['code', 'id', 'name', 'country_id/id']
        self.load(model, load_fields, to_import)

        # Mapping repated data in source
        # __export__.res_country_state_118  ANZ Anzoategui Venezuela  105
        # __export__.res_country_state_87   DC  DC         Venezuela  85
        # __export__.res_country_state_100  TR  TRIPOLI    Lebanon    98
        map_repeated_codes = [
            ('__export__', 'res_country_state_118',
             '__export__.res_country_state_105'),
            ('__export__', 'res_country_state_87',
             '__export__.res_country_state_85'),
            ('__export__', 'res_country_state_100',
             '__export__.res_country_state_98'),
        ]
        for item in map_repeated_codes:
            new_id = self.new_instance.env.ref(item[2]).id
            to_mapping.append([new_id, item[0], item[1]])

        # Mapping states
        fields = ['res_id', 'module', 'name', 'model', 'id']
        values = [state + [model, '_'.join(['dummy', state[2]])]
                  for state in to_mapping]

        dummys = self.load(
            'ir.model.data', fields, values)
        self.dummy_ir_models.extend(dummys.get('ids', []))

    def mapping_res_currency(self):
        """ Will create the dummy xml ids for old currencies
        """
        _logger.info("Mapping Currencies")
        model = 'res.currency'
        fields = ['model', 'res_id', 'id', 'module', 'name']
        values = [
            # MXN
            [model, 34, 'dummy_res_currency_mxn', '__export__',
             'res_currency_193'],
            [model, 34, 'dummy_res_currency_mxn2', '__export__',
             'res_currency_197'],

            # USD
            [model, 3, 'dummy_res_currency_usd', '__export__',
             'res_currency_195'],
            [model, 3, 'dummy_res_currency_usd2', '__export__',
             'res_currency_196'],
        ]
        dummys = self.load(
            'ir.model.data', fields, values)

        self.dummy_ir_models.extend(dummys.get('ids', []))

    def mapping_cleanup(self):
        """ Delete the created ir.model.data records created for avoid
        making individual mapping for each field that refers to:

        - res.company model.
        - project.task.type model

        """
        self.new_instance.execute(
            'ir.model.data', 'unlink', self.dummy_ir_models)

    def write_exported(self, headers, values):
        fname = 'export.csv'
        data = []
        for row in values:
            data.append([
                value.encode("ascii", "ignore").replace(',', '')
                for value in row])
        with open(fname, 'a', newline='') as csvfile:
            wr = csv.writer(csvfile, delimiter=";")
            wr.writerows(data)

    def write_errors(self, model, header, records):
        """ write in migration_errors.csv the list of records that were not
        imported for any error while importing. This way the user will be
        able to fix the error and re imported without mapping again.
        """
        with open(model + '.csv', 'a', newline='') as csvfile:
            wr = csv.writer(csvfile)
            wr.writerow(header)
            wr.writerows(records)

    def migrate_fiscal_position(self, domain=None, limit=None):
        """ Old regiment.fiscal model records to account.fiscal.position
        """
        _logger.info('Migrate Regimen Fiscal as Fiscal Positions')
        read_model = 'regimen.fiscal'
        write_model = 'account.fiscal.position'
        domain = domain or []
        export_fields = [
            'name',
            'id',
            'description',

            'create_date',
            'write_date',
            # 'create_uid/id',
            # 'write_uid/id',

            # len_vat,  # TODO ask if needed
            # TODO review if we need to merge this new fields in
            # account.fiscal.position into old values
            # account.fiscal.position
            # 'auto_apply',
            # 'vat_required',
            # 'sequence',
            # 'zip_from',
            # 'zip_to',
            # 'company_id/id',
            # account_ids, tax_ids, write_uid, create_uid, country_id,
            # country_group_id,
        ]
        load_fields = []
        load_fields.extend(export_fields)
        load_fields[load_fields.index('description')] = 'note'
        position_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info(write_model + " to create %s" % (len(position_ids),))
        position_data = self.export(
            read_model, position_ids, export_fields).get('datas', [])
        self.load(write_model, load_fields, position_data)

    def migrate_res_partner(self, domain=None, limit=None):
        """ This method allow migrate the specific data of the res_partner
        model.
        """
        _logger.info('Migrate Partners')
        model = 'res.partner'
        domain = domain or []
        domain = [
            '|', ('active', '=', False), ('active', '=', True),
            ('id', 'not in', [1, 3])] + domain
        partner_ids = self.legacy.execute(
            model, 'search', domain, 0, limit)
        _logger.info("Partners to migrate %s" % (len(partner_ids),))

        export_fields = [
            'id', 'name', 'activation', 'website_description', 'image_medium',
            'debit_limit', 'signup_token', 'create_date', 'street', 'debit',
            'supplier', 'ref', 'email', 'picking_warn', 'street2', 'active',
            'zip', 'comment', 'sale_warn', 'purchase_warn', 'color', 'image',
            'city', 'type', 'function', 'picking_warn_msg', 'phone',
            'customer', 'vat', 'invoice_warn_msg', 'website', 'sale_warn_msg',
            'invoice_warn', 'is_company', 'write_date', 'date', 'lang',
            'purchase_warn_msg', 'mobile', 'image_small', 'signup_type',
            'date_partnership', 'partner_longitude', 'calendar_last_notif_ack',
            'signup_expiration', 'website_meta_keywords', 'date_review',
            'website_meta_description', 'date_review_next',
            'message_last_post', 'partner_latitude', 'tz', 'employee',
            'website_meta_title', 'website_published', 'opt_out',
            'ean13', 'l10n_mx_street3', 'l10n_mx_street4',
            'l10n_mx_city2', 'nacionality_diot', 'type_of_third',
            'type_of_operation',
            'regimen_fiscal_id/id',
            'parent_id/id',

            # Export relational fields
            'country_id/id', 'company_id/id',

            'credit_limit',  # TODO review value before set

            # TODO test result
            '__last_update', 'website_short_description',

            # TODO import other states not Mexican
            'state_id/id',

            # TODO review. Not imported, will be set with default value
            # 'property_product_pricelist',
            # 'property_stock_supplier',
            # 'property_stock_customer',
            # 'property_supplier_payment_term',
            # 'property_payment_term/id',
            # 'display_name',
            # 'ref_companies/id',

            # TODO review with josemoralesp
            # 'message_ids',

            # TODO test Automatic set when load the users
            # 'user_ids', 'user_id',

            # TODO need to be syncronize with account_reports_followup module
            # TODO review with nhomar
            # 'latest_followup_date',
            # 'latest_followup_level_id',
            # 'latest_followup_level_id_without_lit',
            # 'payment_amount_due',
            # 'payment_amount_overdue',
            # 'payment_earliest_due_date',

            # TODO Need to be set after create partners.
            # 'child_ids', 'message_follower_ids',
            # 'commercial_partner_id',  'implemented_partner_ids',
            # 'assigned_partner_id',

            # TODO Need to be relocated
            # 'birthdate',  # now belong to employee model (bithday)

            # Deprecated fields (NOT EXPORTED)
            # 'country',  # Already have country_id
            # 'city_id/id', # Now use city field (char)
            # 'has_image',  # Compute field not used in saas-14
            # 'issue_count',  # Compute field not used anymore project issue
            # 'section_id',  # Sales teams will not be migrated they will be
            #                # created from scratch
            # 'grade_id',  # will not be migrated
            # notification_email_send

            # Not used in 8.0 and Deprecated in saas-14
            # 'certificate_code',
            # 'last_reconciliation_date',

            # Not needed anymore, now we only use vat field
            # 'vat_split', 'vat_subjected',

            # Were renamed and will not be export since a new default value
            # will # be set manually
            # 'property_account_payable',
            # 'property_account_receivable',

            # 'number_fiscal_id_diot',  # not in saas-14, not used in 8.0
            # 'opportunity_assigned_ids',  # do not exist and is compute
            # 'opportunity_ids',  will be migrated later
            # 'message_summary',
            # 'pay_method_id',
            # 'phonecall_count',  # deleted from crm, enterprise/void ip
            # 'phonecall_ids',  # idem
            # 'property_account_position',
            # 'property_product_pricelist_purchase',  # not in saas-14
            # 'receive_my_emails',  # module vauxoo, not installed by moment
            # 'event_ids',  # will not be imported
            # 'event_registration_ids',  # idem
            # 'speaker',  # does not exist
            # 'unreconciled_aml_ids',  # computed field
            # 'use_parent_address',  # does not exist
            # 'self',  # gamification module will not be migrated

            # Store False
            # 'signup_valid', 'signup_url', 'purchase_order_count',
            # 'journal_item_count', 'parent_name', 'contracts_count',
            # 'supplier_invoice_count', 'credit', 'meeting_count',
            # 'sale_order_count', 'opportunity_count', 'task_count',
            # 'payment_next_action_date', 'payment_next_action',
            # 'message_unread', 'payment_note', 'total_invoiced',
            # 'message_is_follower', 'contact_address', 'tz_offset',

            # Not worthy, are empty
            # 'date_localization',
            # 'partner_weight',

            # This ones will be automatic compute after migrate the records
            # 'contract_ids',
            # 'bank_ids',
            # 'invoice_ids',
            # 'sale_order_ids',
            # 'task_ids',

            # Will be ignored since is not used, not really
            # 'category_id/id',
            # 'meeting_ids/id',
            # 'title/id',

            # Can not be imported, after user imported they can be
            # 'create_uid', 'write_uid',
        ]

        # Prepare load fields
        load_fields = []
        load_fields.extend(export_fields)
        to_rename = [
            ('street', 'street_name'),
            ('l10n_mx_street3', 'street_number'),
            ('l10n_mx_street4', 'street_number2'),
            ('l10n_mx_city2', 'l10n_mx_edi_locality'),
            ('nacionality_diot', 'l10n_mx_nationality'),
            ('type_of_third', 'l10n_mx_type_of_third'),
            ('type_of_operation', 'l10n_mx_type_of_operation'),
            ('regimen_fiscal_id/id', 'property_account_position_id/id'),
            ('ean13', 'barcode'),
            ('is_company', 'company_type'),
        ]
        for item in to_rename:
            load_fields[load_fields.index(item[0])] = item[1]

        type_mapping = dict([
            (r'Default', 'Contact'),
            (r'Invoice', 'Invoice address'),
            (r'Shipping', 'Shipping address'),
            (r'Other', 'Other address'),
        ])
        partner_data = self.export(
            model, partner_ids, export_fields).get('datas', [])

        load_data_group = []

        for (item, partner) in enumerate(partner_data, 1):
            # Set default values
            partner[load_fields.index('company_id/id')] = False
            partner[load_fields.index('website_published')] = False
            partner[load_fields.index('opt_out')] = False

            partner[load_fields.index('credit_limit')] = 0  # necessary?

            # Mapping
            partner[load_fields.index('company_type')] = (
                'company' if partner[load_fields.index('company_type')]
                else 'person')
            partner[load_fields.index('type')] = type_mapping.get(
                partner[load_fields.index('type')])
            partner[load_fields.index('lang')] = self.res_lang_mapping(
                partner[load_fields.index('lang')])
            vat = partner[load_fields.index('vat')]

            generic_vat_to_avoid = [
                'MXXEXX010101000', 'MXEXX010101000', 'MXXAXX010101000',
            ]
            if vat and vat in generic_vat_to_avoid:
                partner[load_fields.index('vat')] = ''
            elif vat and vat[:2] in ['EC', 'ES', 'MX', 'PE', 'VE']:
                partner[load_fields.index('vat')] = vat[2:].strip()
            # payment_term = self.get_value('property_payment_term_id')
            # if payment_term == 'Contado USD BBVA Bancomer':
            #     self.change_value('property_payment_term_id', False)
            country_id = partner[load_fields.index('country_id/id')]
            if country_id == "base.mx":
                load_fields[export_fields.index('street2')] = \
                    'l10n_mx_edi_colony'

            load_data_group.append(partner)

        partner_ids = self.load(
            model, load_fields, load_data_group)

    def migrate_app_categ(self, domain=None, limit=None, defaults=None):
        """ All the application category that has been exported in legacy
        instance
        """
        _logger.info('Migrate Application Categories')
        domain = domain or []
        defaults = defaults or {}
        read_model = write_model = 'ir.module.category'

        domain = domain + [
            ('module', '=', '__export__'), ('model', '=', read_model)]
        model_data_apps = self.legacy.execute(
            'ir.model.data', 'search', domain, 0, limit)

        categ_apps_ids = self.legacy.execute(
            'ir.model.data', 'read', model_data_apps, ['res_id'])
        categ_apps_ids = [item.get('res_id') for item in categ_apps_ids]

        export_fields = load_fields = [
            'id', 'name', 'write_date', 'create_date', 'visible', 'sequence',
            'description',
            # todo review
            # 'parent_id', 'module_ids', 'child_ids',
        ]
        apps_data = self.export(
            read_model, categ_apps_ids, export_fields).get('datas')

        self.load(write_model, load_fields, apps_data)

    def migrate_res_groups(self, domain=None, limit=None, defaults=None):
        """ All the groups that has been exported in legacy instance
        """
        _logger.info('Migrate Groups')
        domain = domain or []
        defaults = defaults or {}
        read_model = write_model = 'res.groups'

        # All groups
        all_groups = self.legacy.execute('res.groups', 'search', [], 0, limit)

        # Search the groups that has not been exported.
        domain = domain + [
            ('module', '!=', '__export__'), ('model', '=', read_model)]
        model_data_groups = self.legacy.execute(
            'ir.model.data', 'search', domain, 0, limit)
        not_exported_groups = self.legacy.execute(
            'ir.model.data', 'read', model_data_groups, ['res_id'])
        not_exported_groups = [
            item.get('res_id') for item in not_exported_groups]

        groups_ids = list(set(all_groups) - set(not_exported_groups))

        export_fields = load_fields = [
            'id', 'name', 'is_portal', 'share',
            'comment', 'create_date', 'write_date', 'implied_ids/id',
            # 'category_id/id',  # not for now
        ]
        groups_data = self.export(
            read_model, groups_ids, export_fields).get('datas')

        for group in groups_data:
            group[load_fields.index('implied_ids/id')] = self.mapping_groups(
                group[load_fields.index('implied_ids/id')])

        self.load(write_model, load_fields, groups_data)

    def migrate_res_users(self, domain=None, limit=None, defaults=None):
        """ This method allow migrate the specific data of the res_users
        model.
        """
        _logger.info('Migrate Users')
        domain = domain or []
        defaults = defaults or {}
        export_fields = [
            # 'state',  TODO map 'Activated:' r'Never Connected', r'Confirmed'

            'id',
            'name',
            'active',
            'company_id/id',
            'company_ids/id',
            'create_date',
            'email',  # related, but not sure if required TODO review
            'lang',
            'login',
            'groups_id/id',
            'implemented_partner_ids/id',
            'karma',
            '__last_update',
            'commercial_partner_id/id',
            'notify_email',
            'oauth_access_token',
            'oauth_provider_id/id',
            'oauth_uid',
            'partner_id/id',
            # 'password',
            'password_crypt',
            'share',
            'signature',
            'write_date',

            # All the next fields were moved to mail.alias model, we do not
            # know if we will use it yet
            # 'alias_id/id',
            # 'alias_contact',
            # 'alias_defaults',
            # 'alias_domain',
            # 'alias_force_thread_id/id',
            # 'alias_model_id/id',
            # 'alias_name',
            # 'alias_parent_model_id/id',
            # 'alias_parent_thread_id/id',
            # 'alias_user_id/id',

            # Not need to be merged. NOT USE / EXIST IN NEW VERSION
            # 'badge_ids/id', 'bronze_badge', 'gold_badge',
            # 'employee_ids/id',
            # 'gmail_password', 'gmail_user',  # Google Account module

            # This two can not be set at least yet because they do not exist
            # 'create_uid/id',
            # 'write_uid/id',

            # This field change name in saas-14, also we agree that the
            # default_section will not be migrated, will be set manually by
            # nhomar
            # 'default_section_id/id',
            # 'section_id/id',

            # is not in user model saas-14 at least
            # 'display_employees_suggestions',
            # 'display_groups_suggestions',

            # TODO need to be syncronize with account_reports_followup module
            # TODO review with nhomar
            # 'latest_followup_date',
            # 'latest_followup_level_id/id',
            # 'latest_followup_level_id_without_lit',
            # 'payment_amount_due',
            # 'payment_amount_overdue',
            # 'payment_earliest_due_date',
            # 'payment_responsible_id/id',

            # Store False / Relation Fields / Compute fields
            # 'login_date', 'activation', 'assigned_partner_id/id',
            # 'bank_ids/id', 'ean13', 'display_name',
            # 'calendar_last_notif_ack', 'category_id/id',
            # 'city', 'color', 'comment', 'contact_address',
            # 'contract_ids/id', 'contracts_count', 'country_id/id', 'credit',
            # 'credit_limit', 'currency_id', 'customer', 'date',
            # 'date_localization', 'date_partnership', 'date_review',
            # 'date_review_next', 'debit', 'debit_limit',
            # 'employee', 'function', 'grade_id/id',
            # 'image', 'image_medium', 'image_small',
            # 'invoice_warn', 'invoice_warn_msg',
            # 'invoice_ids/id', 'is_company', 'journal_item_count',
            # 'l10n_mx_city2', 'l10n_mx_street3', 'l10n_mx_street4',
            # 'has_image',  # Compute field not used in saas-14
            # 'issue_count',  # Compute field not used anymore project issue
            # 'opt_out', 'parent_name', 'partner_latitude',
            # 'partner_longitude', 'partner_weight', 'mobile', 'parent_id/id',
            # 'payment_next_action', 'payment_next_action_date',
            # 'payment_note', 'phone', 'picking_warn', 'picking_warn_msg',
            # 'opportunity_count', 'opportunity_assigned_ids/id'
            # 'property_account_position/id', 'property_payment_term/id',
            # 'property_stock_customer/id', 'property_stock_supplier/id',
            # 'property_supplier_payment_term/id', 'purchase_order_count',
            # 'purchase_warn', 'purchase_warn_msg',
            # 'property_product_pricelist_purchase',  # TODO not in saas-14
            # 'receive_my_emails',  # module vauxoo, not installed by moment
            # 'property_account_payable/id', 'property_account_receivable/id',
            # 'regimen_fiscal_id/id', 'sale_order_count', 'sale_warn',
            # 'sale_warn_msg', 'ref', 'signup_expiration', 'signup_token',
            # 'signup_type', 'signup_url', 'signup_valid', 'silver_badge',
            # 'street', 'street2', 'supplier',
            # 'sale_order_ids/id', 'state', 'state_id/id', 'title',
            # 'total_invoiced', 'supplier_invoice_count', 'tz', 'tz_offset',
            # 'unreconciled_aml_ids/id', 'task_count', # 'task_ids/id',
            # 'type', 'self', 'vat', 'zip', 'website',
            # 'website_description', 'website_meta_description',
            # 'website_meta_keywords', 'website_meta_title',
            # 'website_published', 'website_short_description',
            # 'new_password',

            # 'property_product_pricelist/id', will not be imported, will be
            # set with the default value

            # TODO review with josemoralesp
            # 'message_follower_ids/id', 'message_ids/id',
            # 'message_is_follower', 'message_last_post',
            # 'message_summary', 'message_unread',

            # TODO need to migrated leads firts
            # 'opportunity_ids/id',

            # Gamification module, will not be imported
            # 'pay_method_id/id',

            # Phonecall model does not exist in crm saas-14, this will be
            # discarded by now
            # 'phonecall_count',
            # 'phonecall_ids/id',

            # 'menu_id/id', does not exist in saas-14?
            # 'speaker',  # does  not exist in auth_oauth anymore, review
            # 'survey_id/id', do not exist in ssas-14 same model at least
            # 'use_parent_address',  seems to not be in saas-14
            # 'user_email',  dot not exist in saas-14, TODO review

            # TODO this ones do not exists yet
            # 'user_id/id',
            # 'user_ids/id',

            # Do not exist in saas-14. deprecated
            # 'vat_split',
            # 'vat_subjected',

            # Ignored
            # 'action_id/id',
        ]

        # Prepare load fields
        load_fields = []
        load_fields.extend(export_fields)
        to_rename = [
            ('notify_email', 'notification_type'),
        ]
        for item in to_rename:
            load_fields[load_fields.index(item[0])] = item[1]
        for (field, value) in defaults.items():
            load_fields.append(field)
        notify_mapping = dict([
            (r'none', r'inbox'),
            (r'always', r'email'),
        ])

        # Domain: Active and non active res.users to avoid a problem of a
        # missing record in the registers. Avoid to migrate/update admin,
        # portaltemplate, public user and migration user
        domain = domain + [
            ('id', 'not in', [1, 34, 36, 935]),
            # TODO by the moment do not load the ones with problem
            # ('id', 'not in', [391, 385, 389, 384, 61, 380, 381, 390, 387,
            #  386, 388]),
        ]

        # Dummy mapping for users that are already exist in instance and
        # we do not want to not migrated then but we need that this has been
        # mapped with the old ones to works with project.tasks
        # user Migration saas-14 6 legacy 935
        fields = ['model', 'res_id', 'id', 'module', 'name']
        values = [
            ['res.users', 6, 'dummy_user_01', '__export__', 'res_users_935'],
        ]
        dummys = self.load(
            'ir.model.data', fields, values)
        if not dummys.get('ids', False):
            return
        self.dummy_ir_models.extend(dummys.get('ids', []))

        user_ids = self.legacy.execute('res.users', 'search', domain, 0, limit)
        _logger.info("Users to create %s" % (len(user_ids),))

        user_data = self.export(
            'res.users', user_ids, export_fields).get('datas', [])

        load_data_group = []
        for user in user_data:
            # set default values
            for (field, value) in defaults.items():
                user.append(value)
            # Pre process
            user[load_fields.index('lang')] = self.res_lang_mapping(
                user[load_fields.index('lang')])
            user[load_fields.index('groups_id/id')] = self.mapping_groups(
                user[load_fields.index('groups_id/id')])
            user[load_fields.index('notification_type')] = \
                notify_mapping.get(
                    user[load_fields.index('notification_type')])
            # Defaults
            user[load_fields.index('company_ids/id')] = 'base.main_company'
            user[load_fields.index('company_id/id')] = 'base.main_company'
            load_data_group.append(user)

        user_ids = self.load(
            'res.users', load_fields, load_data_group)

    def migrate_employee(self, domain=None, limit=None, defaults=None):
        """ Migrate only the employee name
        """
        _logger.info('Migrate Employees basic')
        domain = domain or []
        defaults = defaults or {}
        read_model = write_model = 'hr.employee'
        export_fields = load_fields = [
            'id',
            'name',
            'user_id/id',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
            'address_home_id/id',
            'address_id/id',
            'image',
            'image_small',
            'image_medium',
        ]

        employee_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("Employees to create %s" % (len(employee_ids),))
        employee_data = self.export(
            read_model, employee_ids, export_fields).get('datas', [])
        self.load(write_model, load_fields, employee_data)

    def migrate_project_stages(self):
        """ Create and mapping project stages.

        The stages used in version 8.0 will not be longer used, new set of
        simple stages will be used.

        In order to make the migrate of the rest of the data in the database
        that depends of this stages we do a dummy ir.model.data records to
        make this mapping faster

        The new project stages we will have are
        Will load the new project stages from the data in the csv fiels
        And will create dummy ir.model.data xml to mapping all the imported
        tasks.

        # 1 New       project.project_stage_data_0
        # 2 Backlog   project.project_stage_data_1
        # 3 WIP       project.project_stage_data_2
        # 4 Done      vauxoo_migration_project_stage_done.project_stage_done
        # 5 Cancelled vauxoo_migration_project_stage_cancelled
        """
        _logger.info('Migrate Project Stages')
        # Read csv with new stages
        stages = []
        with open("project_task_type.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            header = False
            for row in reader:
                if not header:
                    header = row
                else:
                    stages.append(row)

        # Load project.tasks.type
        stages_data = self.load(
            'project.task.type', header, stages)

        _logger.info(pprint.pformat(stages_data))

    def mapping_project_stages(self):
        """ After we update the database the references to old stages in
        project and project_conf module will be automatic deleted and the
        tasks will be leave as undefined. In order to avoid this we need to
        Change all the created tasks to the proper new stage so this stages
        dont set to Undefined.
        """
        new = 'project.project_stage_data_0'
        backlog = 'project.project_stage_data_1'
        wip = 'project.project_stage_data_2'
        done = 'vauxoo_migration_project_stage_done'
        waiting_customer = 'vauxoo_migration_project_stage_waiting_cust'
        waiting_expert = 'vauxoo_migration_project_stage_waiting_expert'
        cancelled = 'vauxoo_migration_project_stage_cancelled'

        self.mapping_project_stage = dict([
            ('__export__.project_task_type_12', new),
            ('__export__.project_task_type_18', new),
            ('project_conf.project_tt_backlog', backlog),
            ('__export__.project_task_type_19', wip),
            ('project.project_tt_analysis', wip),
            ('project.project_tt_design', wip),
            ('project.project_tt_development', wip),
            ('__export__.project_task_type_21', wip),
            ('__export__.project_task_type_22', wip),
            ('__export__.project_task_type_25', wip),
            ('project.project_tt_merge', wip),
            ('project.project_tt_specification', wip),
            ('project.project_tt_testing', wip),
            ('project_conf.project_tt_leader', wip),
            ('__export__.project_task_type_15', waiting_customer),
            ('__export__.project_task_type_16', waiting_expert),
            ('__export__.project_task_type_17', wip),
            ('project.project_tt_deployment', done),
            ('__export__.project_task_type_26', done),
            ('project.project_tt_cancel', cancelled),
        ])

        # Mapping old user story states
        self.story_state = {
            'New': ('project.project_stage_data_0', 'Grey'),
            'In Progress': ('project.project_stage_data_2', 'Grey'),
            'Pending': ('project.project_stage_data_2', 'Green'),
            'Done': ('vauxoo_migration_project_stage_done', 'Grey'),
            'Cancelled': ('vauxoo_migration_project_stage_cancelled', 'Grey'),
        }

    def mapping_project_tags(self):
        """ Create Orphan Tasks tag add dummy mapping"""
        _logger.info("Mapping orphan task tag")
        model = 'project.tags'
        tag = {
            'id': 'vauxoo_migration_orphan_task_tag',
            'name': 'Orphan Task',
            'color': 4,
        }
        self.load(model, list(tag.keys()), [list(tag.values())])

        # Mapping repated data in source
        self.map_repeated('project.tags', [
            # bug tag
            ('project_category_100', 'project_category_220'),
            # rma yani tag
            ('project_category_152', 'project_category_153'),
            # ventas
            ('project_category_66', 'project_category_170'),
            # compras tag
            ('project_category_97', 'project_category_165'),
            ('project_category_97', 'project_category_168'),
            ('project_category_97', 'project_category_184'),
            # production tag
            ('project_category_64', 'project_category_65'),
        ])

        # Mapping repated data in source
        self.map_repeated('helpdesk.tag', [
            # 7.0 tag
            ('project_category_89_htag', 'project_category_183_htag'),
            # compras tag
            ('project_category_97_htag', 'project_category_124_htag'),
            ('project_category_97_htag', 'project_category_125_htag'),
            ('project_category_97_htag', 'project_category_130_htag'),
            # ('project_category_97_htag', 'project_category_169'),
            # 7.0 tag
            ('project_category_89_htag', 'project_category_183_htag'),
            ])

    def migrate_tags(self, write_model, domain=None, limit=None,
                     defaults=None):
        read_model = 'project.category'
        defaults = defaults or {}

        _logger.info("Migrate Project Tags (%s as %s)" % (
            read_model, write_model))

        domain = domain or []
        domain = domain + [
            # Avoid repeated tags, this one will be mapped. one empty discarded
            ('id', 'not in', [65, 124, 125, 130, 165, 168, 169, 184, 183, 220,
                              153, 170])]
        tag_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("tags to create %s" % (len(tag_ids),))
        export_fields = [
            'id', 'name',
            'create_date', 'write_date',
            'create_uid/id', 'write_uid/id',
        ]
        load_fields = []
        load_fields.extend(export_fields)
        load_fields.append('color')

        export_data = self.export(
            read_model, tag_ids, export_fields).get('datas', [])
        # preprocess
        load_data_group = []
        for (index, tag) in enumerate(export_data, 0):
            # defaults
            tag.append(1)
            load_data_group.append(tag)
            suffix = defaults.get('suffix', '')
            tag[0] = tag[0] + suffix

        self.load(write_model, load_fields, load_data_group)

    def map_repeated(self, model, values):
        """ Mapping repated data in source """
        to_mapping = []
        fields = ['res_id', 'module', 'name', 'model', 'id']
        for item in values:
            new_id = self.new_instance.env.ref('__export__.' + item[0]).id
            to_mapping.append(
                [new_id, '__export__', item[1], model,
                 '_'.join(['dummy', item[1]])])
        dummys = self.load(
            'ir.model.data', fields, to_mapping)
        self.dummy_ir_models.extend(dummys.get('ids', []))

    def load_and_run(self, server_action_file):
        write_model = 'ir.actions.server'
        data = []
        with open(server_action_file, "r") as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            data = [row for row in reader]

        loaded_data = self.load(
            write_model, header, data)

        self.new_instance.execute(
            write_model, 'run', loaded_data.get('ids', False))

    def migrate_project_task(self, domain=None, limit=None, defaults=None):
        _logger.info('Migrate Project Tasks')
        read_model = write_model = 'project.task'
        domain = domain or []
        defaults = defaults or {}
        domain = domain + ['|', ('active', '=', False), ('active', '=', True)]
        task_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("Tasks to create %s" % (len(task_ids),))
        export = ['id', 'name', 'active', 'color', 'date_end',
                  'date_start', 'date_deadline', 'delay_hours',
                  'description', 'effective_hours', 'kanban_state',
                  'notes', 'planned_hours', 'progress',
                  'remaining_hours', 'partner_id/id', 'company_id/id',
                  'user_id/id', 'stage_id/id', 'sequence',
                  'userstory_id/id', 'sprint_id/id', 'priority',
                  'project_id/id',
                  'parent_id/id',
                  'total_hours',
                  'create_date', 'create_uid/id',
                  'write_date', 'write_uid/id',
                  'date_last_stage_update',
                  'categ_ids/id',
                  '.id']
        load_fields = []
        load_fields.extend(export)

        # Mapping
        load_fields[export.index('userstory_id/id')] = 'list_id/id'
        load_fields[export.index('project_id/id')] = 'group_id/id'

        # Remove not to import
        load_fields.remove('.id')
        load_fields.remove('categ_ids/id')
        load_fields.remove('sprint_id/id')

        load_fields.append('date_assign')
        load_fields.append('tag_ids/id')
        load_fields.append('project_id/id')

        task_data = self.export(
            read_model, task_ids, export).get('datas', [])
        load_data_group = []
        for (item, task) in enumerate(task_data):
            # Mapping
            legacy_id = task[export.index('.id')]
            task[export.index('name')] = \
                task[export.index('name')] + " [T" + legacy_id + "]"
            kanban_st_mapping = dict([
                (r'In Progress', 'Grey'),
                (r'Blocked', 'Red'),
                (r'Ready for next stage', 'Green')])
            task[export.index('kanban_state')] = \
                kanban_st_mapping.get(
                    task[export.index('kanban_state')])
            priority_mapping = dict([
                (r'Normal', 'Low'),
                (r'Low', 'Low'),
                (r'High', 'Normal')])
            task[export.index('priority')] = \
                priority_mapping.get(task[export.index('priority')])
            task[export.index('stage_id/id')] = \
                self.mapping_project_stage.get(
                    task[export.index('stage_id/id')])
            task.append(task[export.index('date_start')])  # date_assign

            sprint = task[export.index('sprint_id/id')] or ''
            category = task[export.index('categ_ids/id')] or ''
            extra_tag = defaults.get('tag_ids/id') \
                if 'tag_ids/id' in defaults else ''
            tags = ','.join([sprint, category, extra_tag])
            tag_ids = ','.join([item for item in tags.split(',') if item])
            task.append(tag_ids)

            task.append(defaults.get('project_id/id'))

            # cleaun up not used to be loaded fields
            task.pop(export.index('.id'))
            task.pop(export.index('categ_ids/id'))
            task.pop(export.index('sprint_id/id'))

            # pprint.pprint(self.list2dict(load_fields, task))

            load_data_group.append(task)

        task_ids = self.load(
            write_model, load_fields, load_data_group)

    def migrate_helpdesk_team(self):
        _logger.info('Create Helpdesk team')
        write_model = 'helpdesk.team'
        load_fields = [
            'id', 'name', 'use_alias', 'use_website_helpdesk_form',
            'use_rating', 'alias_name', 'project_id/id', 'website_published']

        support_team = 'vauxoo_migration_support_team'
        load_data_group = [
            ['helpdesk.helpdesk_team1', 'Support', 'True', 'True', 'True',
             'support', support_team, 'True'],
            ['vauxoo_migration_infrastructure_support_team', 'Infrastructure',
             'True', 'True', 'True', 'infrastructure', support_team, 'True'],
        ]
        self.load(write_model, load_fields, load_data_group)

    def migrate_helpdesk_stages(self):
        """ Create new helpdesk stages

        # New       vauxoo_migration_helpdesk_stage_new
        # WIP       helpdesk.stage_in_progress
        # Waiting Customer Feed.. vauxoo_migration_helpdesk_stage_waiting_cust
        # Waiting Expert Feed.. vauxoo_migration_helpdesk_stage_waiting_expert
        # Done      helpdesk.stage_solved
        # Cancelled helpdesk.stage_cancelled
        """
        _logger.info('Migrate Helpdesk Stage')
        # Read csv with new stages
        stages = []
        with open("helpdesk_stage.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            header = False
            for row in reader:
                if not header:
                    header = row
                else:
                    stages.append(row)

        # Load helpdesk stage
        stages_data = self.load(
            'helpdesk.stage', header, stages)

        _logger.info(pprint.pformat(stages_data))

    def mapping_helpdesk_stages(self):
        """ Create and mapping helpdesk stages.
        #   New                     project.project_stage_data_0
        # 2 In Progress             project.project_stage_data_1
        #   Waiting Cust Feedback   project.project_stage_data_2
        # 3 Done                    vauxoo.project_stage_done
        # 4 Cancelled               vauxoo.project_stage_cancelled

        """
        # TODO need to make special kaban status for the next registers
        # TODO need to process the stages of the helpdesk apart using this ones
        read_model = 'project.task.type'
        write_model = 'helpdesk.stage'
        _logger.info("Mapping Project Stages of support (%s as %s)" % (
            read_model, write_model))

        new = 'vauxoo_migration_helpdesk_stage_new'
        waiting_customer = 'vauxoo_migration_helpdesk_stage_waiting_cust'
        waiting_expert = 'vauxoo_migration_helpdesk_stage_waiting_expert'
        done = 'helpdesk.stage_solved'
        cancelled = 'helpdesk.stage_cancelled'
        wip = 'helpdesk.stage_in_progress'

        self.mapping_helpdesk_stage = dict([
            ('__export__.project_task_type_18', new),   # New
            ('project.project_tt_deployment', done),    # Done
            ('__export__.project_task_type_26', done),  # Finished
            ('project.project_tt_cancel', cancelled),   # Cancelled
            ('__export__.project_task_type_19', wip),   # In Progress
            ('project.project_tt_merge', wip),          # Merge
            ('project_conf.project_tt_leader', wip),    # Testing Leader
            ('__export__.project_task_type_17', wip),   # Waiting Odoo Feedback
            ('__export__.project_task_type_15', waiting_customer),
            # Waiting Cust Feedback
            ('__export__.project_task_type_16', waiting_expert),
            # Waiting Expert Feed..
        ])

    def migrate_project_issue(self, domain=None, limit=None, defaults=None):
        read_model = 'project.issue'
        write_model = 'helpdesk.ticket'
        domain = domain or []
        defaults = defaults or {}

        _logger.info("Migrate Project Issues (%s as %s)" % (
            read_model, write_model))

        domain = domain + ['|', ('active', '=', False), ('active', '=', True)]
        issue_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("issues to create %s" % (len(issue_ids),))
        export_fields = [
            'id', 'name', 'active', 'description',
            'partner_id/id', 'user_id/id',
            'color',
            # 'project_id/id',
            'stage_id/id',
            'kanban_state', 'priority',
            'task_id/id',
            'create_date', 'write_date',
            'create_uid/id', 'write_uid/id',
            'categ_ids/id',
            '.id',
        ]
        load_fields = []
        load_fields.extend(export_fields[:-1])
        # load_fields[load_fields.index('project_id/id')] = 'tag_ids'
        load_fields[load_fields.index('categ_ids/id')] = 'tag_ids/id'
        load_fields.append('team_id/id')
        load_fields.append('ticket_type_id/id')

        export_data = self.export(
            read_model, issue_ids, export_fields).get('datas', [])

        load_data_group = []
        for issue in export_data:
            # Mapping
            legacy_id = issue.pop(export_fields.index('.id'))
            name = issue[load_fields.index('name')]
            issue[load_fields.index('name')] = \
                name + " [PI" + str(legacy_id) + "]"
            task = issue[load_fields.index('task_id/id')] or str()
            issue[load_fields.index('task_id/id')] = task
            priority_mapping = dict([
                (r'Low', 'All'),
                (r'Normal', 'Low priority'),
                (r'High', 'High priority'),
            ])
            issue[load_fields.index('priority')] = priority_mapping.get(
                issue[load_fields.index('priority')])
            issue[load_fields.index('stage_id/id')] = \
                self.mapping_helpdesk_stage.get(
                    issue[load_fields.index('stage_id/id')])
            tags = issue[load_fields.index('tag_ids/id')] or str()
            issue[load_fields.index('tag_ids/id')] = ','.join(
                [item + '_htag' for item in tags.split(',') if item])

            # defaults
            issue.append(defaults.get('team_id/id'))
            issue.append('helpdesk.type_incident')

            load_data_group.append(issue)

        self.load(write_model, load_fields, load_data_group)

    def migrate_user_story(self, domain=None, limit=None, defaults=None):
        """Migrate user_stories as tasks were project is another task"""
        read_model = 'user.story'
        write_model = 'project.task'
        domain = domain or []
        defaults = defaults or {}

        _logger.info("Migrate Customers User Stories (%s as %s)" % (
            read_model, write_model))

        export_fields = [
            'id', 'name', 'user_id/id', '.id',

            # data necessary to set te customer
            'owner_id/id',  # TODO where to add this important data
            'project_id/partner_id/id',

            # 'user_execute_id/id',  # TODO review
            'description', 'info', 'asumption', 'implementation',
            'create_date', 'write_date',
            'create_uid/id', 'write_uid/id',
            'sprint_ids/id', 'project_id/id', 'project_id/name',
            'state',
            # 'task_ids/id',
            # 'approved',
            # 'priority_level',
            'planned_hours',
            # 'sk_id',
            'categ_ids/id',
            # 'accep_crit_ids/ids',
            # 'display_name',  # TODO  Is not set sad face
        ]

        load_fields = [
            'id',
            'name',
            'partner_id/id',
            'owner_id/id',
            'description',
            'gap',
            'asumption',
            'implementation',
            'project_id/id',
            'group_id/id',
            'tag_ids/id',
            'stage_id/id',
            'kanban_state',
            'planned_hours',
            'user_id/id',
            'create_date',
            'create_uid/id',
            'write_date',
            'write_uid/id',
        ]

        story_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("User Stories to create " + str(len(story_ids)))

        export_data = self.export(
            read_model, story_ids, export_fields).get('datas', [])
        user_story_data = [self.list2dict(export_fields, item)
                           for item in export_data]

        load_data_group = []
        # preprocessing data
        for user_story in user_story_data:
            stage, kanban_state = self.story_state.get(
                user_story.get('state'))
            tags = ','.join([
                user_story.get('sprint_ids/id') or str(),
                user_story.get('categ_ids/id') or str()
            ])
            tag_ids = ','.join([item for item in tags.split(',') if item])
            group_id = user_story.get('project_id/id')

            user_story.update(defaults)
            task = [
                user_story.get('id'),
                user_story.get('name') + " [US%s]" % user_story.get('.id'),
                user_story.get('project_id/partner_id/id'),  # partner_id
                user_story.get('owner_id/id'),
                user_story.get('description'),
                user_story.get('info'),  # gap
                user_story.get('asumption'),
                user_story.get('implementation'),
                user_story.get('project_id/id'),  # project_id (team)
                group_id,  # task (old project_id)
                tag_ids,
                stage,
                kanban_state,
                user_story.get('planned_hours'),
                user_story.get('user_id/id'),
                user_story.get('create_date'),
                user_story.get('create_uid/id'),
                user_story.get('write_date'),
                user_story.get('write_uid/id'),
            ]
            load_data_group.append(task)

        self.load(write_model, load_fields, load_data_group)

    def migrate_sprint(self, domain=None, limit=None):
        """ Method to migrate sprint model as project_tag"""
        read_model = 'sprint.kanban'
        write_model = 'project.tags'
        _logger.info("Migrate Sprints (%s as %s)" % (
            read_model, write_model))

        domain = domain or []
        export_fields = [
            'id',
            'name',
            'color',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]

        sprint_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("--- Sprints to create %s" % (len(sprint_ids),))

        load_fields = export_fields
        sprint_data = self.export(
            read_model, sprint_ids, export_fields).get('datas', [])

        load_data_group = []
        for sprint in sprint_data:
            if 'sprint' not in sprint[load_fields.index('name')].lower():
                sprint[load_fields.index('name')] = 'Sprint - ' + \
                    sprint[load_fields.index('name')]
            sprint[load_fields.index('color')] = 5
            load_data_group.append(sprint)

        self.load(write_model, load_fields, load_data_group)

    def migrate_user_story_difficulty(self, limit=None):
        """ Method to migrate user.story.difficulty as project.tags"""
        read_model = 'user.story.difficulty'
        write_model = 'project.tags'
        _logger.info("Migrate User Story Difficulty (%s as %s)" % (
            read_model, write_model))

        export_fields = [
            'id',
            'name',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]
        story_ids = self.legacy.execute(read_model, 'search', [], 0, limit)
        _logger.info("-- User Stories Tags to create %s" % (len(story_ids),))

        load_fields = []
        load_fields.extend(export_fields)
        story_data = self.export(
            read_model, story_ids, export_fields).get('datas', [])
        self.load(write_model, load_fields, story_data)

    def migrate_acceptability_criteria(self, domain=None, limit=None,
                                       defaults=None):
        """ Method to migrate acceptability.criteria model as project.task"""
        _logger.info("Migrate Acceptability Criteria as Tasks")
        read_model = 'acceptability.criteria'
        write_model = 'project.task'

        domain = domain or []
        defaults = defaults or {}
        export_fields = [
            'id',
            'name',
            '.id',
            'scenario',
            'sprint_id/id',
            'development',
            'difficulty_level/id',
            'user_id/id',
            'create_date',
            'write_date',
            'accep_crit_id/id',
            'project_id/id',
            'sequence_ac',
            'accep_crit_id/project_id/partner_id/id',
            'categ_ids/id',
            'create_uid/id',
            'write_uid/id',
            # TODO review this with Katherine
            # 'accep_crit_state',
            # 'difficulty', 'display_name', 'project_id', 'sequence',
            # 'sk_id', 'us_ac_numbers',
            'user_execute_id/id',
            'accepted',
            'accep_crit_id/owner_id/id',
        ]

        load_fields = [
            'id',
            'name',
            'description',
            'tag_ids/id',
            'stage_id/id',
            'user_id/id',
            'create_date',
            'write_date',
            'list_id/id',  # user story
            'group_id/id',  # old project_id
            'project_id/id',
            'sequence',
            'partner_id/id',
            'create_uid/id',
            'write_uid/id',
            'accepted',
            'owner_id/id',
            'layer_id/id',
        ]

        record_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info(read_model + " to export %s" % (len(record_ids),))

        export_data = self.export(
            read_model, record_ids, export_fields).get('datas', [])
        criteria_data = [self.list2dict(export_fields, item)
                         for item in export_data]
        load_data_group = []

        # preprocessing data
        for criteria in criteria_data:
            sprint = criteria.get('sprint_id/id') or ''
            difficulty = criteria.get('difficulty_level/id') or ''
            category = criteria.get('categ_ids/id') or ''
            tags = ','.join([
                tag for tag in [sprint, difficulty] + category.split(',')
                if tag])
            stage = ('project.project_stage_data_2'
                     if criteria.get('development') else
                     'project.project_stage_data_0')
            group_id = criteria.get('project_id/id')

            criteria.update(defaults)
            task = [
                criteria.get('id'),
                criteria.get('name') + " [AC" + criteria.get('.id') + "]",
                criteria.get('scenario'),  # description
                tags,
                stage,
                criteria.get('user_execute_id/id'),
                criteria.get('create_date'),
                criteria.get('write_date'),
                criteria.get('accep_crit_id/id'),  # User Story (list_id)
                group_id,  # Old Project
                criteria.get('project_id/id'),
                criteria.get('sequence_ac') or 10,
                criteria.get('accep_crit_id/project_id/partner_id/id'),
                criteria.get('create_uid/id'),
                criteria.get('write_uid/id'),
                criteria.get('accepted'),
                criteria.get('accep_crit_id/owner_id/id'),
                '__export__.project_task_migration_01',
            ]
            load_data_group.append(task)
        # pprint.pprint(
        # [self.list2dict(load_fields, item) for item in load_data_group])
        self.load(write_model, load_fields, load_data_group)

    def migrate_project_teams(self, domain=None, limit=None):
        """ Will load the new project teams from csv file and will
        create/updates records of project.project. model
        """
        _logger.info('Migrate project teams')
        # TODO this method is really similar to migrate_project_stages and can
        # be modularitate in some way to be reused
        write_model = 'project.project'
        data = []
        with open("project_project.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            header = False
            for row in reader:
                if not header:
                    header = row
                else:
                    data.append(row)
        self.load(write_model, header, data)

        # Set up sub tasks projects
        load_fields = ['id', 'subtask_project_id/id']
        values = [['vauxoo_migration_research_development_team',
                   'vauxoo_migration_research_development_team']]
        self.load(write_model, load_fields, values)

    def mapping_layer(self):
        """ Create a task of type layer that all the tasks will be related on
        """
        _logger.info('Mapping layer')
        write_model = 'project.task'
        load_fields = ['id', 'name']
        load_data = [['__export__.project_task_migration_01', 'Layer 1']]
        self.load(write_model, load_fields, load_data)

    def migrate_sale_orders(self, domain=None, limit=None):
        _logger.info('Migration sale orders')
        read_model = write_model = 'sale.order'
        export_fields = [
            'id',
            'name',
            'partner_id/id',
            'date_order',
            'state',
            'client_order_ref',
            'note',
            'picking_policy',
            'user_id/id',
            'company_id/id',
            'origin',
            'currency_id',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
            # TODO Ask nhomar
            # 'categ_ids/id',  # Tags m2m(crm.case.categ)
            # 'medium_id/id',  # Channel m2o(crm.tracking.medium)
        ]
        load_fields = []
        load_fields.extend(export_fields)
        # load_fields[export_fields.index('categ_ids/id')] = 'tag_ids/id'

        sale_ids = self.legacy.execute(read_model, 'search', domain, 0, limit)
        _logger.info(write_model + " to migrate %s" % (len(sale_ids),))
        export_data = self.export(
            read_model, sale_ids, export_fields).get('datas', [])

        load_data_group = []
        # preprocessing data
        for record in export_data:
            # Mapping
            state_mapping = dict([
                (r'Draft Quotation', r'Quotation'),
                (r'Quotation Sent', r'Quotation Sent'),
                (r'Sale to Invoice', r'Sales Order'),
                (r'Sales Order', r'Sales Order'),
                (r'Invoice Exception', r'Sales Order'),
                (r'Done', r'Locked'),
                (r'Cancelled', r'Cancelled'),
            ])
            record[load_fields.index('state')] = state_mapping.get(
                record[load_fields.index('state')])
            load_data_group.append(record)

        self.load(write_model, load_fields, load_data_group)
        return sale_ids

    def migrate_analytic_account(self, domain=None, limit=None):
        _logger.info('Migration sale orders')
        read_model = write_model = 'sale.order'
        export_fields = [
            'id',
            'name',
            'code',
            'create_date',
            'create_uid/id',
            # 'crossovered_budget_line/id',  # TODO ask nhomar
            # 'line_ids',  # TODO
            'partner_id/id',
            # 'project_ids/id'  # TODO .... ujum...
            'write_date',
            'write_uid/id',
        ]

        load_fields = []
        load_fields.extend(export_fields)
        # load_fields[export_fields.index('categ_ids/id')] = 'tag_ids/id'

        sale_ids = self.legacy.execute(read_model, 'search', domain, 0, limit)
        _logger.info(write_model + " to migrate %s" % (len(sale_ids),))
        export_data = self.export(
            read_model, sale_ids, export_fields).get('datas', [])

        load_data_group = []
        # preprocessing data
        for record in export_data:
            state_mapping = dict([
                (r'Draft Quotation', r'Quotation'),
                (r'Quotation Sent', r'Quotation Sent'),
                (r'Sale to Invoice', r'Sales Order'),
                (r'Sales Order', r'Sales Order'),
                (r'Invoice Exception', r'Sales Order'),
                (r'Done', r'Locked'),
                (r'Cancelled', r'Cancelled'),
            ])
            record[4] = state_mapping.get(record[4])
            load_data_group.append(record)

        self.load(write_model, load_fields, load_data_group)
        return sale_ids

    def migrate_leads_sources(self, domain=None, limit=None):
        _logger.info('Migrate Leads Sources')
        read_model = 'crm.tracking.source'
        write_model = 'utm.source'
        domain = domain or []
        export_fields = [
            'id',
            'name',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]

        load_fields = []
        load_fields.extend(export_fields)

        # Avoid to import sources that need to be mapped
        domain = domain + [('id', 'not in', [1, 2, 3, 6])]
        source_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info(write_model + " to migrate %s" % (len(source_ids),))
        export_data = self.export(
            read_model, source_ids, export_fields).get('datas', [])

        self.load(write_model, load_fields, export_data)

        # Mapping the sources that are with different xml in saas-14
        fields = ['res_id', 'module', 'name', 'model', 'id']
        to_mapping = [
            # Search Engine (utm.utm_source_search_engine)
            [1, 'crm', 'crm_source_search_engine'],
            [1, '__export__', 'crm_tracking_source_6'],
            # Mailing Partner (utm.utm_source_mailing)
            [2, 'crm', 'crm_source_mailing'],
            # Newsletter (utm.utm_source_newsletter)
            [3, 'crm', 'crm_source_newsletter'],
        ]
        values = [source + [write_model, '_'.join(['dummy', source[2]])]
                  for source in to_mapping]
        dummys = self.load(
            'ir.model.data', fields, values)
        self.dummy_ir_models.extend(dummys.get('ids', []))

    def migrate_leads_stages(self, domain=None, limit=None):
        _logger.info('Migrate Leads Stages')
        read_model = 'crm.case.stage'
        write_model = 'crm.stage'
        domain = domain or []
        export_fields = [
            'id',
            'name',
            'create_date', 'create_uid/id',
            'fold',
            'on_change',
            'probability',
            'requirements',
            'sequence',
            'write_date', 'write_uid/id',
            # 'type',
            # 'state',
        ]

        load_fields = []
        load_fields.extend(export_fields)

        stage_ids = self.legacy.execute(read_model, 'search', domain, 0, limit)
        _logger.info(write_model + " to migrate %s" % (len(stage_ids),))

        export_data = self.export(
            read_model, stage_ids, export_fields).get('datas', [])
        self.load(write_model, load_fields, export_data)

    def migrate_leads(self, domain=None, limit=None):
        _logger.info('Migrate Leads')
        read_model = write_model = 'crm.lead'
        domain = domain or []
        export_fields = [
            '.id',
            'name',
            'active',
            # 'campaign_id/id'
            'city',
            'color',
            # 'company_id/id',  # TODO review
            'contact_name',
            'country_id/id',
            'create_date', 'create_uid/id',
            'date_action_last',
            'date_assign',
            'date_closed',
            'date_deadline',
            'date_last_stage_update',
            'date_open',
            'day_close',
            'day_open',
            'description',
            'email_cc',
            'email_from',
            'function',
            'message_bounce',
            'mobile',
            'opt_out',  # TODO ask nhomar
            # 'partner_address_email'  # Does not exist anymore
            # 'partner_address_name'  # Does not exist anymore
            'partner_assigned_id/id',
            'partner_id/id',
            'partner_latitude',
            'partner_longitude',
            'partner_name',
            'phone',
            'planned_revenue',
            'priority',
            'probability',
            # 'ref', 'ref2',  # TODO seems like they do not exist in saas-14
            'referred',
            # 'section_id'  # Ignored in purpose
            'source_id/id',  # TODO ask nhomar and alejandro
            'stage_id/id',
            'state_id/id',
            # 'status',  # deprecated
            'street',
            'street2',
            # 'title',  # this model records will be ignored
            # 'title_action',  # deprecated
            'type',
            'user_id/id',
            'write_date', 'write_uid/id',
        ]

        load_fields = [
            'id',
            'name',
            'active',
            # 'campaign_id'
            'city',
            'color',
            # 'company_id',  # TODO review
            'contact_name',
            'country_id',
            'create_date', 'create_uid',
            'date_action_last',
            'date_assign',
            'date_closed',
            'date_deadline',
            'date_last_stage_update',
            'date_open',
            'day_close',
            'day_open',
            'description',
            'email_cc',
            'email_from',
            'function',
            'message_bounce',
            'mobile',
            'opt_out',  # TODO ask nhomar
            # 'partner_address_email'  # Does not exist anymore
            # 'partner_address_name'  # Does not exist anymore
            'partner_assigned_id',
            'partner_id',
            'partner_latitude',
            'partner_longitude',
            'partner_name',
            'phone',
            'planned_revenue',
            'priority',
            'probability',
            # 'ref', 'ref2',  # TODO seems like they do not exist in saas-14
            'referred',
            # 'section_id'  # Ignored in purpose
            'source_id',  # TODO ask nhomar and alejandro
            'stage_id',
            'state_id',
            # 'status',  # deprecated
            'street',
            'street2',
            # 'title',  # this model records will be ignored
            # 'title_action',  # deprecated
            'type',
            'user_id',
            'write_date', 'write_uid',
        ]

        lead_ids = self.legacy.execute(read_model, 'search', domain, 0, limit)
        _logger.info(write_model + " to migrate %s" % (len(lead_ids),))

        mapping_priority = dict([
            ('Very Low', 'Low'),
            ('Low', 'Low'),
            ('Normal', 'Normal'),
            ('High', 'High'),
            ('Very High', 'Very High'),
        ])

        record_data = self.export(read_model, lead_ids, export_fields)
        xml_ids = defaultdict()
        for (item, record) in enumerate(record_data.get('datas', []), 1):
            for field in load_fields:
                if not (field.endswith('_id') or field.endswith('_uid')):
                    continue
                index = load_fields.index(field)
                xml_ids[record[index]] = record[index] and xml_ids.get(
                    record[index], False) or record[index] and (
                    self.new_instance.execute(
                        'ir.model.data', 'xmlid_to_res_id',
                        record[index]) or None) or None
                record[index] = xml_ids[record[index]]

            # Mapping
            record[load_fields.index('priority')] = mapping_priority.get(
                record[load_fields.index('priority')])

            record = [self.clean_str(i) for i in record]
            dict_vals = dict(zip(load_fields, record))
            insert = self.cr.mogrify("""
            INSERT INTO crm_lead (
            id,name,active,city,color,contact_name,country_id,create_date,
            create_uid,date_action_last,date_assign,date_closed,
            date_deadline,date_last_stage_update,date_open,day_close,day_open,
            description,email_cc,email_from,function,message_bounce,mobile,
            opt_out,partner_assigned_id,partner_id,partner_latitude,
            partner_longitude,partner_name,phone,planned_revenue,priority,
            probability,referred,source_id,stage_id,state_id,street,street2,
            type,user_id,write_date,write_uid) VALUES
            (%(id)s,%(name)s,%(active)s,%(city)s,%(color)s,%(contact_name)s,
            %(country_id)s,%(create_date)s,%(create_uid)s,%(date_action_last)s,
            %(date_assign)s,%(date_closed)s,%(date_deadline)s,
            %(date_last_stage_update)s,%(date_open)s,%(day_close)s,
            %(day_open)s,%(description)s,%(email_cc)s,%(email_from)s,
            %(function)s,%(message_bounce)s,%(mobile)s,%(opt_out)s,
            %(partner_assigned_id)s,%(partner_id)s,%(partner_latitude)s,
            %(partner_longitude)s,%(partner_name)s,%(phone)s,%(planned_revenue)s,
            %(priority)s,%(probability)s,%(referred)s,%(source_id)s,%(stage_id)s,
            %(state_id)s,%(street)s,%(street2)s,%(type)s,%(user_id)s,
            %(write_date)s,%(write_uid)s)
            """, dict_vals)
            self.cr.execute(insert)
            self.cr.execute('SELECT max(id) FROM crm_lead')
            last_id = self.cr.fetchall()
            last_id = last_id[0][0] if last_id else False
            self.cr.execute('ALTER SEQUENCE crm_lead_id_seq RESTART WITH %s',
                            (last_id + 1, ))
        # loaded_data = self.load(
            # write_model, load_fields, load_data_group)

    def migrate_sale_order_lines(self, domain=None, limit=None):
        _logger.info('Migration sale orders lines')
        read_model = write_model = 'sale.order.line'
        export_fields = [
            'id',
            'name',
            'price_unit',
            'product_uom_qty',
            'state',
            'order_id/id',
            'product_id/id',
            'product_uom/id',
            # customer_lead,  # required in saas-14, review
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]
        load_fields = []
        load_fields.extend(export_fields)
        ids = self.legacy.execute(read_model, 'search', domain, 0, limit)
        _logger.info(write_model + " to migrate %s" % (len(ids),))
        export_data = self.export(
            read_model, ids, export_fields).get('datas', [])

        load_data_group = []
        # preprocessing data
        for record in export_data:
            state_mapping = dict([
                (r'Draft', r'Quotation'),
                (r'Draft', r'Quotation Sent'),
                (r'Confirmed', r'Sales Order'),
                (r'Exception', r'Sales Order'),
                (r'Done', r'Locked'),
                (r'Cancelled', r'Cancelled'),
            ])
            record[load_fields.index('state')] = state_mapping.get(
                record[load_fields.index('state')])
            load_data_group.append(record)
        self.load(write_model, load_fields, load_data_group)

    def migrate_project_project(self, domain=None, limit=None, defaults=None):
        """ Create task for each project.project """
        domain = domain or []
        defaults = defaults or {}
        read_model = 'project.project'
        write_model = 'project.task'
        _logger.info("Migrate Projects (%s as %s)" % (
            read_model, write_model))

        export_fields = [
            'id', 'name', 'partner_id/id', 'user_id/id', 'date_start',
            'currency_id/id', 'descriptions',
            # 'state', TODO need mapping
            'create_date', 'write_date',
            'create_uid/id', 'write_uid/id',
            # task_ids,  # TODO important
            # 'analytic_account_id', 'analytic_account_id/id',
            # # TODO review this with Nhomar
            # 'privacy_visiblity', 'use_timesheets',
            # 'use_issues', 'members',
            # analytic_account_id, planned_hours, effective_hours, date_start,
            # sequence, currency_id, parent_id, type_ids (stages),
            # task_ids,
            '.id',
        ]

        load_fields = [
            'id',
            'name',
            'partner_id/id',
            'user_id/id',
            'date_start',
            'currency_id/id',
            'description',
            # 'stage_id/id',
            'project_id/id',
            'create_date', 'write_date',
            'create_uid/id', 'write_uid/id',
        ]

        project_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)

        _logger.info(read_model + " to migrate %s" % (len(project_ids),))
        export_data = self.export(
            read_model, project_ids, export_fields).get('datas', [])
        projects = [self.list2dict(export_fields, item)
                    for item in export_data]

        task_data = []

        # preprocessing data
        for project in projects:
            project.update(defaults)
            task = [
                project.get('id'),
                project.get('name') + " [P%s]" % str(project.get('.id')),
                project.get('partner_id/id'),
                project.get('user_id/id'),
                project.get('date_start'),
                project.get('currency_id/id'),
                project.get('descriptions'),
                project.get('project_id/id', False),
                project.get('create_date'),
                project.get('write_date'),
                project.get('create_uid/id'),
                project.get('write_uid/id'),
            ]
            task_data.append(task)
        self.load(write_model, load_fields, task_data)

    def mapping_invoice_rate(self):
        """ Mapping the Invoice rate """
        _logger.info("Mapping Invoice Rate")
        model = 'hr_timesheet_invoice.factor'
        fields = ['model', 'res_id', 'id', 'module', 'name']
        values = [
            [model, '1', 'dummy_factor_01', 'hr_timesheet_invoice',
             'timesheet_invoice_factor1'],
            [model, '2', 'dummy_factor_02', 'hr_timesheet_invoice',
             'timesheet_invoice_factor2'],
            [model, '3', 'dummy_factor_03', '__export__',
             'hr_timesheet_invoice_factor_7'],
            [model, '4', 'dummy_factor_04', 'hr_timesheet_invoice',
             'timesheet_invoice_factor4'],
            [model, '5', 'dummy_factor_05', 'hr_timesheet_invoice',
             'timesheet_invoice_factor3'],
            [model, '6', 'dummy_factor_06', '__export__',
             'hr_timesheet_invoice_factor_6'],
            [model, '7', 'dummy_factor_07', '__export__',
             'hr_timesheet_invoice_factor_5'],
        ]
        dummys = self.load(
            'ir.model.data', fields, values)
        self.dummy_ir_models.extend(dummys.get('ids', []))

    @staticmethod
    def clean_str(val):
        return val or None

    def migrate_timesheets(self, domain=None, limit=None, defaults=None):
        """ Method to migrate timesheets get together old models """
        read_model = 'project.task.work'
        write_model = 'account.analytic.line'

        _logger.info("Migrate timesheets (%s as %s)" % (
            read_model, write_model))

        domain = domain or []
        defaults = defaults or {}
        export_fields = [
            'hr_analytic_timesheet_id/.id',
            '.id',
            'name',
            'task_id/id',
            'create_date', 'write_date',
            'create_uid/id', 'write_uid/id',

            'hr_analytic_timesheet_id/to_invoice/id',
            'hr_analytic_timesheet_id/unit_amount',
            'hr_analytic_timesheet_id/amount',
            'date',
            'task_id/partner_id/id',
            'hr_analytic_timesheet_id/user_id/id',
            'task_id/project_id/id',
            'hr_analytic_timesheet_id/currency_id/id',

            # 'userstory_id',
            # 'hr_analytic_timesheet_id/account_id/id',

            # TODO hr_analytic_timesheet that need to reviewed if need migrate
            # 'journal_id/id',
            # 'percentage', 'product_id', 'amount_currency',
            # 'product_uom_id/id',
            # 'issue_id', 'ref', 'sheet_id', 'move_id',
            # 'invoice_id', 'code'
            # NOT migrate
            # 'invoiceables_hours', compute('to_invoice', 'unit_amount')
            # 'general_account_id/id', nhomar saud is not needed
        ]
        load_fields = [
            'name',
            'task_id',
            'create_date',
            'write_date',
            'create_uid',
            'write_uid',
            'to_invoice',
            'unit_amount',
            'amount',
            'date',
            'partner_id',
            'user_id',
            'project_id',
            'currency_id',
            'account_id',
        ]

        record_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        click.echo(read_model + "to export %s" % (len(record_ids),))
        record_data = self.export(read_model, record_ids, export_fields)

        # time_file = open('/tmp/hr_timesheet.csv', 'wb')
        # query = self.cr.mogrify(
        #     """COPY account_analytic_line(%s)
        #     FROM STDIN WITH DELIMITER '|' NULL AS 'null' CSV QUOTE "" """,
        #     (AsIs(','.join(load_fields)),))
        xml_ids = defaultdict()
        for (item, record) in enumerate(record_data.get('datas', []), 1):
            old_id_hr = record[0]
            record.pop(0)
            old_id_task = record[0]
            record.pop(0)
            for field in load_fields:
                if not ((field.endswith('_id') or field.endswith('_uid') or
                        field == 'to_invoice') and field != 'account_id'):
                    continue
                index = load_fields.index(field)
                xml_ids[record[index]] = record[index] and xml_ids.get(
                    record[index], False) or record[index] and (
                    self.new_instance.execute(
                        'ir.model.data', 'xmlid_to_res_id',
                        record[index]) or None) or None
                record[index] = xml_ids[record[index]]
            # todo by now, all the timesheets will have implementation
            # project/analytic account
            index = load_fields.index('amount')
            record[index] = record[index] or 0.0
            index = load_fields.index('unit_amount')
            record[index] = record[index] or 0.0
            record[load_fields.index('project_id')] = defaults.get(
                'project_id/.id')
            record.append(defaults.get('account_id/.id'))
            dict_vals = dict(zip(load_fields, record))
            qry = self.cr.mogrify("""
                    INSERT INTO account_analytic_line (
                                  name,task_id,create_date,write_date,
                                  create_uid,write_uid,to_invoice,
                                  unit_amount,amount,date,partner_id,
                                  user_id,project_id,currency_id,
                                  account_id) VALUES
                                  (%(name)s,%(task_id)s,%(create_date)s,
                                  %(write_date)s,%(create_uid)s,
                                  %(write_uid)s,%(to_invoice)s,
                                  %(unit_amount)s,%(amount)s,%(date)s,
                                  %(partner_id)s,%(user_id)s,%(project_id)s,
                                  %(currency_id)s,%(account_id)s) RETURNING id
                                  """, dict_vals)
            self.cr.execute(qry)
            new_id = self.cr.fetchall()
            new_id = new_id[0] if new_id else False
            self.cr.execute(
                """
            INSERT INTO ir_model_data
            (name, noupdate, date_init, date_update, module, model, res_id)
                VALUES
            ('analytic_timesheet_v8_'||%s, true, NOW(), NOW(), '__export__',
            'account.analytic.line', %s);
                """, (old_id_hr or (str(old_id_task) + '_task'), new_id))
            # time_file.write('|'.join(map(self.clean_str, record)) + '\n')
        # time_file.close()
        # time_file = open('/tmp/hr_timesheet.csv', 'rb')
        # self.cr.copy_expert(query, time_file)

    def migrate_product_public_category(self, domain=None, limit=None):
        """ Method to migrate product.public.category model """
        read_model = 'product.public.category'
        write_model = 'product.public.category'
        domain = domain or []

        export_fields = [
            'id', 'name',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]

        pub_categ_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit
        )
        _logger.info("-- Public categories to create %s" % (
            len(pub_categ_ids),))
        load_fields = export_fields
        pub_categ_data = self.export(
            read_model, pub_categ_ids, export_fields).get('datas', [])

        load_data_group = []
        for (item, pub_categ) in enumerate(pub_categ_data, 1):
            load_data_group.append(pub_categ)

        self.load(write_model, load_fields, load_data_group)

    def migrate_product_attribute(self, domain=None, limit=None):
        """ Method to migrate product.attribute model """
        read_model = 'product.attribute'
        write_model = 'product.attribute'
        domain = domain or []

        export_fields = [
            'id', 'name',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]
        attribute_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("-- Attributes to create %s" % (len(attribute_ids),))
        load_fields = export_fields
        attribute_data = self.export(
            read_model, attribute_ids, export_fields).get('datas', [])

        self.load(write_model, load_fields, attribute_data)

    def migrate_product_attribute_value(self, domain=None, limit=None):
        """ Method to migrate product.attribute.value model """
        read_model = 'product.attribute.value'
        write_model = 'product.attribute.value'
        domain = domain or []

        export_fields = [
            'id', 'name', 'attribute_id/id',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]

        value_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("-- Attributes values to create %s" % (len(value_ids),))

        load_fields = export_fields
        value_data = self.export(
            read_model, value_ids, export_fields).get('datas', [])
        self.load(write_model, load_fields, value_data)

    def migrate_product_category(self, domain=None, limit=None):
        """ Method to migrate product.category model """
        read_model = 'product.category'
        write_model = 'product.category'
        domain = domain or []

        export_fields = [
            'id', 'name',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]
        prod_cat_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("-- Product categories to create %s" % (
            len(prod_cat_ids),))
        load_fields = export_fields
        prod_cat_data = self.export(
            read_model, prod_cat_ids, export_fields).get('datas', [])
        load_data_group = []
        for (item, prod_cat) in enumerate(prod_cat_data, 1):
            load_data_group.append(prod_cat)

        self.load(write_model, load_fields, load_data_group)

    def migrate_product_uom_categ(self, domain=None, limit=None):
        """ Method to migrate product.uom.categ model """
        read_model = 'product.uom.categ'
        write_model = 'product.uom.categ'
        domain = domain or []

        export_fields = [
            'id', 'name',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]
        categ_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("--- Uom categories to create %s" % (len(categ_ids),))
        load_fields = export_fields
        categ_data = self.export(
            read_model, categ_ids, export_fields).get('datas', [])
        load_data_group = []
        for (item, categ) in enumerate(categ_data, 1):
            load_data_group.append(categ)

        self.load(write_model, load_fields, load_data_group)

    def migrate_product_uom(self, domain=None, limit=None):
        """ Method to migrate product.uom model """
        read_model = 'product.uom'
        write_model = 'product.uom'
        domain = domain or []

        export_fields = [
            'id', 'name', 'uom_type', 'rounding', 'factor', 'factor_inv',
            'category_id/id',
            'create_date', 'create_uid/id',
            'write_date', 'write_uid/id',
        ]

        uom_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("--- Uom to create %s" % (len(uom_ids),))
        load_fields = export_fields
        uom_data = self.export(
            read_model, uom_ids, export_fields).get('datas', [])
        load_data_group = []
        for (item, uom) in enumerate(uom_data, 1):
            load_data_group.append(uom)

        self.load(write_model, load_fields, load_data_group)

    def migrate_product_template(self, domain=None, limit=None):
        """ Method to migrate product.template model """
        read_model = 'product.template'
        write_model = 'product.template'
        domain = domain or []

        export_fields = [
            'id', 'name', 'image', 'image_medium', 'image_small', 'active',
            'event_ok', 'purchase_ok', 'sale_ok', 'website_published',
            'default_code', 'website_meta_keywords', 'website_meta_title',
            'create_date', 'message_last_post', 'write_date', 'list_price',
            'sale_delay', 'volume', 'website_description',
            'color', 'website_sequence', 'website_size_x',
            'description_purchase', 'description_sale', 'purchase_line_warn',
            'purchase_line_warn_msg', 'sale_line_warn_msg', 'website_size_y',
            'website_meta_description', 'sale_line_warn', 'type',
            'description', 'company_id/id', 'create_uid/id', 'write_uid/id',
            'uom_id/id', 'uom_po_id/id', 'categ_id/id',
            'public_categ_ids/id',

            # TODO This fields will be enabled once we have the related records
            # 'accessory_product_ids',
            # 'alternative_product_ids',
            # 'website_style_ids',

            # TODO This fields do not exist in saas14
            # 'ean13',
            # 'loc_case',
            # 'loc_rack',
            # 'loc_row',
            # 'hr_expense_ok',
            # 'is_product_variant',
            # 'track_all',
            # 'track_incoming',
            # 'uos_coeff',
            # 'track_outgoing',
            # 'qty_available_text',
            # 'seller_qty',
            # 'mes_type',
            # 'weight_net',
            # 'state',
            # 'message_summary',
            # 'event_type_id',
            # 'product_manager',
            # 'uos_id',

            # TODO fields with new name in saas14
            # 'property_account_expense'
            # 'property_account_income'

            # TODO review this fields
            # 'taxes_id',
            # 'supplier_taxes_id',
            # 'attribute_line_ids',
            # 'message_ids',
            # 'seller_ids',
            # 'website_message_ids',
            # 'cost_method',
            # 'valuation',
            # 'message_follower_ids',
            # 'seller_ids',
            # 'packaging_ids',
            # 'product_variant_ids',
            # 'price',
            # 'standard_price',
            # 'pricelist_id',
            # 'property_stock_account_input',
            # 'property_stock_account_output',
        ]
        load_fields = []
        load_fields.extend(export_fields)

        domain = ['|', ('active', '=', False), ('active', '=', True)] + domain
        product_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit)
        _logger.info("- Products Template to create %s" % (len(product_ids),))
        product_data = self.export(
            read_model, product_ids, export_fields).get('datas', [])
        load_data_group = []
        for product in product_data:
            # defaults
            product[load_fields.index('company_id/id')] = False
            product[load_fields.index('website_published')] = False
            load_data_group.append(product)

        self.new_instance.env.context.update(
            {'create_product_product': True})
        self.new_instance.env[write_model].load(
            load_fields, load_data_group)

    def migrate_product_product(self, domain=None, limit=None):
        """ Method to migrate product.product model """
        read_model = 'product.product'
        write_model = 'product.product'
        domain = domain or []

        export_fields = [
            'id', 'name', 'image', 'image_medium', 'image_small', 'active',
            'event_ok', 'purchase_ok', 'sale_ok', 'website_published',
            'default_code', 'website_meta_keywords', 'website_meta_title',
            'create_date', 'message_last_post', 'write_date', 'list_price',
            'sale_delay', 'volume', 'website_description',
            'color', 'website_sequence', 'website_size_x',
            'description_purchase', 'description_sale', 'purchase_line_warn',
            'purchase_line_warn_msg', 'sale_line_warn_msg', 'website_size_y',
            'website_meta_description', 'sale_line_warn', 'type',
            'description', 'company_id/id', 'create_uid/id', 'write_uid/id',
            'uom_id/id', 'uom_po_id/id', 'categ_id/id', 'product_tmpl_id/id',
            'price', 'standard_price', 'price_extra',
            'attribute_value_ids/id',
        ]
        load_fields = []
        load_fields.extend(export_fields)

        domain = ['|', ('active', '=', False), ('active', '=', True)] + domain
        prod_prod_ids = self.legacy.execute(
            read_model, 'search', domain, 0, limit
        )
        _logger.info("- Products to create %s" % (len(prod_prod_ids),))
        prod_prod_data = self.export(
            read_model, prod_prod_ids, export_fields).get('datas', [])
        load_data_group = []
        for prod in prod_prod_data:
            # defaults
            prod[load_fields.index('company_id/id')] = False
            prod[load_fields.index('website_published')] = False
            load_data_group.append(prod)

        self.load(write_model, load_fields, load_data_group)

    def get_tasks(self, projects):
        read_model = 'project.task'
        domain = [('project_id', 'in', projects), ('issue_id', '=', False)]
        tasks_ids = self.legacy.execute(read_model, 'search', domain)
        return tasks_ids

    def get_issue_tasks(self):
        read_model = 'project.task'
        domain = [('issue_id', '!=', False)]
        tasks_ids = self.legacy.execute(read_model, 'search', domain)
        return tasks_ids

    def get_tags(self, model):
        tasks = self.legacy.execute(
            model, 'search', [('categ_ids', '!=', False)])
        tags = self.export(model, tasks, ['categ_ids/.id']).get('datas')
        tag_ids = []
        for item in tags:
            tag_ids.extend(item[0].split(','))
        tag_ids = list(set([int(item) for item in tag_ids]))
        return tag_ids

    def get_customer_projects(self):
        read_model = 'project.project'
        user_stories = self.legacy.execute('user.story', 'search', [])
        projects_w_stories = self.export(
            'user.story', user_stories, ['project_id/.id'])
        projects_w_stories = list(
            set([int(item[0]) for item in projects_w_stories.get('datas')]))
        domain = [
            ('id', 'in', projects_w_stories),
            ('partner_id', '!=', False),
            ('partner_id', 'not in', [1, 3, 26, 4, 5156])]
        project_ids = self.legacy.execute(read_model, 'search', domain)
        return project_ids

    def get_sales_to_export(self):
        read_model = 'sale.order'
        sales = self.legacy.execute(read_model, 'search', [
            ('company_id', '=', 1)])
        return sales

    def get_internal_projects(self):
        read_model = 'project.project'
        domain = ['|', ('partner_id', '=', False),
                  ('partner_id', 'in', [1, 3, 26, 4, 5156])]
        # The next partners are considered internal projects: Partner Vauxoo
        # Odoo Partner, Vauxoo Admin, Nhomar Hernandez, Alejandro Negrin
        project_ids = self.legacy.execute(read_model, 'search', domain)
        return project_ids

    def load_csv(self, csvfile):
        """ receive a csvfile with already prepare and mapped record and try to
        re load into instance.
        """
        with open(csvfile, 'r') as csvfilefile:
            rd = csv.reader(csvfilefile)
            data = list(rd)

        model = csvfile.replace('.csv', '')
        self.load(model, data[0], data[1:])

    def migrate_per_model(self, model, domain=None, defaults=None,
                          context=None):
        """ Run migration for only one model and set of ids.
        """
        domain = domain and eval(domain) or []
        defaults = defaults and eval(defaults) or {}
        context = context and eval(context) or {}

        if model == 'project.task':
            self.migrate_project_task(
                domain, defaults=defaults)
        elif model == 'user.story':
            self.mapping_project_stages()
            self.migrate_user_story(domain=domain, defaults=defaults)
        elif model == 'acceptability.criteria':
            self.migrate_acceptability_criteria(
                domain=domain, defaults=defaults)
        elif model == 'sale.order.line':
            sales_to_export = self.get_sales_to_export()
            self.migrate_sale_order_lines([
                ('order_id', 'in', sales_to_export),
                # TODO This ones has been commented we have a problem not
                # detected yet
                ('id', 'not in', [1008, 1361, 1718, 2212]),
            ])


class Config(dict):
    def __init__(self, *args, **kwargs):
        self.config = py.path.local(
            click.get_app_dir('vxmigration')
        ).join('config.json')

        super(Config, self).__init__(*args, **kwargs)

    def load(self):
        """load a JSON config file from disk"""
        try:
            self.update(json.loads(self.config.read()))
        except py.error.ENOENT:
            pass

    def save(self):
        self.config.ensure()
        with self.config.open('w') as configfile:
            configfile.write(json.dumps(self))


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    _logger.info('version: %s' % __version__)
    ctx.exit()


def conect_and_login(host, port, db, user, pwd, odoo=True):
    if odoo:
        instance = odoorpc.ODOO(host, port=port, timeout=9999999)
        instance.login(db, user, pwd)
        _logger.info(
            "Connected to database %s (%s) in host %s:%s as %s" % (
                db, instance.version, host, port, user))
    else:
        instance = psycopg2.connect(
            host=host, user=user, password=pwd, port=port, dbname=db)
    return instance


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.command()
@click_log.simple_verbosity_option()
@click.option('--legacy-host', default='127.0.0.1',
              help='Od oo server host. default 127.0.0.1')
@click.option('--legacy-port', type=int, default=8069,
              help='O doo server port. default 8069')
@click.option("--legacy-db", type=str, help='Database name')
@click.option("--legacy-user", type=str, help='Odoo user')
@click.option("--legacy-pwd", type=str, help='Odoo user password')
@click.option('--nhost', default='127.0.0.1',
              help='Odoo  server host. default 127.0.0.1')
@click.option('--nport', type=int, default=8069,
              help='Odoo server port. default 8069')
@click.option("--ndb", type=str, help='Database name')
@click.option("--nuser", type=str, help='Odoo user')
@click.option("--npwd", type=str, help='Odoo user password')
@click.option('--save-config', is_flag=True)
@click.option('--show-config', is_flag=True, help='Show config file')
@click.option('--use-config', is_flag=True, help='Use config file for params')
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show version and exit')
@click.option('--dbhost', default='127.0.0.1',
              help='Odoo  DB server host. default 127.0.0.1')
@click.option('--dbport', type=int, default=5432,
              help='Odoo DB server port. default 5432')
@click.option("--dbuser", type=str, help='DB user')
@click.option("--dbpwd", type=str, help='DB user password')
@click.option('--model', type=str, help="migrate the records of the model")
@click.option('--domain', type=str, help="migrate the records in domain")
@click.option('--defaults', type=str, help="Default values for migrated"
              " records")
@click.option('--context', type=str, help="Context to use in migration."
              " Example: internal")
@click.option('--load-csv', type=str, help="CSV w/records to retry load.")
@pass_config
def main(config, save_config, show_config, use_config,
         legacy_host=None, legacy_port=None, legacy_db=None, legacy_user=None,
         legacy_pwd=None, nhost=None, nport=None, ndb=None, nuser=None,
         npwd=None,
         model=None, domain=None, defaults=None, context=None,
         load_csv=None,
         dbhost=None, dbport=None, dbuser=None, dbpwd=None):
    """ This tools with let us to import from/export to 8.0 to saas-14

    First parameters correspond to the legacy instance,
    Parameters with --n prefix are the ones of the new instance where the
    data will be migrate.
    """
    if show_config:
        config.load()
        _logger.info(pprint.pformat(config))
        quit()
    if save_config:
        config.update(
            legacy_host=legacy_host, legacy_port=legacy_port,
            legacy_db=legacy_db, legacy_user=legacy_user,
            legacy_pwd=legacy_pwd,
            nhost=nhost, nport=nport, ndb=ndb, nuser=nuser, npwd=npwd,
            dbhost=dbhost, dbport=dbport, dbuser=dbuser, dbpwd=dbpwd
        )
        config.save()
        _logger.info(pprint.pformat(config))
        _logger.info(
            "Configuration saved in " + str(click.get_app_dir('vxmigration')))
        quit()
    if use_config:
        config.load()
        legacy_host = config.get('legacy_host')
        legacy_port = config.get('legacy_port')
        legacy_db = config.get('legacy_db')
        legacy_user = config.get('legacy_user')
        legacy_pwd = config.get('legacy_pwd')
        nhost = config.get('nhost')
        nport = config.get('nport')
        ndb = config.get('ndb')
        nuser = config.get('nuser')
        npwd = config.get('npwd')
        dbhost = config.get('dbhost')
        dbport = config.get('dbport')
        dbuser = config.get('dbuser')
        dbpwd = config.get('dbpwd')

    if legacy_db is None or ndb is None or legacy_user is None or \
       nuser is None or legacy_pwd is None or npwd is None:
        if legacy_db is None or ndb is None:
            _logger.error("Both legacy and new databases are required")
        if legacy_user is None or nuser is None:
            _logger.error("Both legacy and new odoo users are required")
        if legacy_pwd is None or npwd is None:
            _logger.error("Both legacy and new odoo passwords are required")
        quit()

    legacy = conect_and_login(legacy_host, legacy_port, legacy_db, legacy_user,
                              legacy_pwd)
    saas14 = conect_and_login(nhost, nport, ndb, nuser, npwd)
    cursor = conect_and_login(dbhost, dbport, ndb, dbuser, dbpwd, False)

    vauxoo = Migration(legacy, saas14, cursor.cursor(), 12, 100)
    vauxoo.test()

    if model:
        vauxoo.migrate_per_model(model, domain, defaults, context)
        quit()
    if load_csv:
        vauxoo.load_csv(load_csv)
        quit()

    # Mapping
    vauxoo.res_company_mapping()

    # # All res.partners
    vauxoo.res_country_state_mapping()
    vauxoo.migrate_fiscal_position()
    _logger.info('Migrate partners without parent_id')
    vauxoo.migrate_res_partner([
        ('parent_id', '=', False),
        ('id', 'not in', [
            # partners realted to the administrator user and the companies
            1,  # Vauxoo Odoo Partner Company Partner
            3,  # Vauxoo Admin admin Partner
            39,  # Vauxoo CA Company Partner
            4342,  # Vat error talk with @nhomar
        ])])
    _logger.info('Migrate partners with parent_id')
    vauxoo.migrate_res_partner([('parent_id', '!=', False)])

    # # Users
    # # vauxoo.migrate_app_categ()
    vauxoo.migrate_res_groups()
    _model, portal = vauxoo.legacy.execute(
        'ir.model.data', 'get_object_reference', 'base', 'group_portal')

    # # Internal Users (active)
    vauxoo.migrate_res_users(
        [('groups_id', 'not in', [portal]), ('active', '=', True)],
        defaults={'notification_type': r'email'})
    # Internal Users (in active)
    vauxoo.migrate_res_users(
        [('groups_id', 'not in', [portal]), ('active', '=', False)],
        defaults={'notification_type': r'inbox'})
    # Portal Users
    vauxoo.migrate_res_users(
        [('groups_id', 'in', [portal]),
         '|', ('active', '=', True), ('active', '=', False)],
        defaults={'groups_id/id': 'base.group_portal',
                  'notification_type': r'inbox'})
    vauxoo.migrate_employee()

    # Products
    vauxoo.migrate_product_attribute()
    vauxoo.migrate_product_attribute_value()
    vauxoo.migrate_product_public_category()
    vauxoo.migrate_product_category()
    vauxoo.migrate_product_uom_categ()
    vauxoo.migrate_product_uom()
    vauxoo.migrate_product_template()
    vauxoo.migrate_product_product()

    # Sale Order
    sales_to_export = vauxoo.get_sales_to_export()
    vauxoo.migrate_sale_orders([('id', 'in', sales_to_export)])
    # TODO we have a problem that need to ve solved with string and bool on
    # date field.
    # vauxoo.migrate_sale_order_lines([
    #   ('order_id', 'in', sales_to_export),
    #   # TODO This ones has been commented we have a problem not detected yet
    #   ('id', 'not in', [1008, 1361, 1718, 2212]),
    # ])
    # vauxoo.migrate_analytic_account()

    # Leads
    vauxoo.migrate_leads_sources()
    vauxoo.migrate_leads_stages()
    vauxoo.migrate_leads()

    # Projects Basic
    vauxoo.migrate_project_teams()
    vauxoo.migrate_project_stages()
    vauxoo.mapping_invoice_rate()  # required for timesheets
    vauxoo.mapping_res_currency()
    vauxoo.mapping_layer()

    # Project Tags
    project_tags = vauxoo.get_tags('project.task') + \
        vauxoo.get_tags('user.story') + \
        vauxoo.get_tags('acceptability.criteria')
    helpdesk_tags = vauxoo.get_tags('project.issue')
    only_project_tags = list(set(project_tags) - set(helpdesk_tags))
    only_helpdesk_tags = list(set(helpdesk_tags) - set(project_tags))
    both_tags = list(set(helpdesk_tags).intersection(set(project_tags)))
    vauxoo.migrate_tags('project.tags', [('id', 'in', only_project_tags)])
    vauxoo.migrate_tags('project.tags', [('id', 'in', both_tags)])
    vauxoo.migrate_tags('helpdesk.tag',
                        [('id', 'in', only_helpdesk_tags + both_tags)],
                        defaults={'suffix': '_htag'})
    vauxoo.mapping_project_tags()
    vauxoo.migrate_sprint()
    vauxoo.migrate_user_story_difficulty()

    # Mapping project and tasks for all the records in project
    vauxoo.mapping_project_stages()
    customer_projects = vauxoo.get_customer_projects()
    customer_team = 'vauxoo.implementation_team'
    internal_projects = vauxoo.get_internal_projects()
    internal_team = '.vauxoo_migration_research_development_team'

    # Projects
    vauxoo.migrate_project_project(
        [('id', 'in', customer_projects)],
        defaults={'project_id/id': customer_team})
    vauxoo.migrate_project_project(
        [('id', 'in', internal_projects)],
        defaults={'project_id/id': customer_team})

    # User Stories
    vauxoo.migrate_user_story(
        [('project_id', 'in', customer_projects)],
        defaults={'project_id/id': customer_team})
    vauxoo.migrate_user_story(
        [('project_id', 'in', internal_projects)],
        defaults={'project_id/id': internal_team})

    # Acceptability Criteria
    vauxoo.migrate_acceptability_criteria(
        [('project_id', 'in', customer_projects)],
        defaults={'project_id/id': customer_team})
    vauxoo.migrate_acceptability_criteria(
        [('project_id', 'in', internal_projects)],
        defaults={'project_id/id': internal_team})

    # Tasks
    customer_tasks = vauxoo.get_tasks(customer_projects)
    vauxoo.migrate_project_task(
        [('id', 'in', customer_tasks),
         ('userstory_id', '!=', False)],
        defaults={'project_id/id': customer_team})
    orphan_tasks = [
        ('id', 'in', customer_tasks),
        ('userstory_id', '=', False)]
    vauxoo.migrate_project_task(orphan_tasks, defaults={
        'project_id/id': customer_team,
        'tag_ids/id': 'vauxoo_migration_orphan_task_tag'})

    internal_tasks = vauxoo.get_tasks(internal_projects)
    vauxoo.migrate_project_task(
        [('id', 'in', internal_tasks),
         ('userstory_id', '!=', False)],
        defaults={'project_id/id': internal_team})
    orphan_tasks = [
        ('id', 'in', internal_tasks),
        ('userstory_id', '=', False)]
    vauxoo.migrate_project_task(orphan_tasks, defaults={
        'project_id/id': internal_team,
        'tag_ids/id': 'vauxoo_migration_orphan_task_tag'})

    # Timesheets
    customer_team_id = vauxoo.new_instance.env.ref(customer_team)
    customer_analytic_id = vauxoo.new_instance.env.ref(
        customer_team + '_account_analytic_account')
    vauxoo.migrate_timesheets(
        [('task_id', 'in', customer_tasks)],
        defaults={'project_id/.id': customer_team_id.id,
                  'account_id/.id': customer_analytic_id.id})

    internal_team_id = vauxoo.new_instance.env.ref(internal_team)
    internal_analytic_id = vauxoo.new_instance.env.ref(
        internal_team + '_account_analytic_account')
    vauxoo.migrate_timesheets(
        [('task_id', 'in', internal_tasks)],
        defaults={'project_id/.id': internal_team_id.id,
                  'account_id/.id': internal_analytic_id.id})

    # # Issues, Issue Projects and Stages
    support_team = '.vauxoo_migration_support_team'
    support_team_id = vauxoo.new_instance.env.ref(support_team)
    support_analytic_id = vauxoo.new_instance.env.ref(
        support_team + '_account_analytic_account')
    helpdesk_team = 'helpdesk.helpdesk_team1'
    issue_tasks = vauxoo.get_issue_tasks()
    vauxoo.migrate_project_task(
        [('id', 'in', issue_tasks)],
        defaults={'project_id/id': support_team})
    vauxoo.migrate_helpdesk_team()
    vauxoo.migrate_helpdesk_stages()
    vauxoo.mapping_helpdesk_stages()
    vauxoo.migrate_project_issue(
        defaults={'team_id/id': helpdesk_team})
    vauxoo.migrate_timesheets(
        [('task_id', 'in', issue_tasks)],
        defaults={'project_id/.id': support_team_id.id,
                  'account_id/.id': support_analytic_id.id})

    _logger.info('Compute tasks display name')
    vauxoo.load_and_run('server_action_display_name.csv')

    _logger.info('Compute tasks spent hours')
    vauxoo.load_and_run('server_action_tasks_spent_hours.csv')

    _logger.info('Update tasks tickets')
    vauxoo.load_and_run('server_action_update_task_ticket.csv')

    # vauxoo.mapping_cleanup()
    cursor.commit()

    _logger.info('Migration script finish')


if __name__ == '__main__':
    main()
