# !/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import csv
import logging
from odoo_csv_tools.import_threaded import import_data
from odoo_csv_tools.export_threaded import export_data


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

    def install_magic_patch(self, magic_user):
        Module = self.new_instance.env['ir.module.module']
        item = 'magic_patch'
        # Get the module ids by name
        module_ids = Module.search([['name', '=', item]])

        # there should be 1 module in module_ids, but iterate for each module
        # object
        for module in Module.browse(module_ids):
            if module.state == 'installed':
                # If installed, just print that it has install
                _logger.info("%s has already been installed.", module.name)
            else:
                # Otherwise, install it
                _logger.debug("Installing %s ... ", module.name)
                module.button_immediate_install()
                _logger.debug("Done.")
        uid = self.new_instance.env['res.users'].search(
            [('login', '=', magic_user)])
        magic_uid = self.new_instance.env.ref(
            'magic_patch.default_magic_user')
        self.new_instance.env['ir.config_parameter'].write(
            magic_uid.ids, {'value': uid[0]})
        magic_active = self.new_instance.env.ref(
            'magic_patch.default_magic_active')
        self.new_instance.env['ir.config_parameter'].write(
            magic_active.ids, {'value': True})

    def uninstall_magic_patch(self):
        Module = self.new_instance.env['ir.module.module']
        item = 'magic_patch'
        module_ids = Module.search([['name', '=', item]])
        for module in Module.browse(module_ids):
            if module.state == 'uninstalled':
                # If installed, just print that it has install
                _logger.info("%s has already been Uninstalled.", module.name)
            else:
                # Otherwise, install it
                _logger.debug("Uninstalling %s ... ", module.name)
                module.button_immediate_uninstall()
                _logger.debug("Done.")

    def load(self, model, load_fields, load_data_group):
        messages, fails, ids = import_data(
            registry=self.new_instance, model=model,
            header=load_fields, data=load_data_group,
            max_connection=self.max_connection, batch_size=self.batch_size)

        if not ids:
            self.write_errors('import.' + model, load_fields, load_data_group)
        return {'failed': fails, 'messages': messages, 'ids': ids}

    def import_data(self, model, load_fields, load_data_group):
        load_data_batchs, batchs = self.chunks(load_data_group)
        loaded_data = {'ids': [], 'messages': []}
        for (group, batch) in enumerate(load_data_batchs, 1):
            _logger.debug("Group %s-%s", group, batchs)
            res = self.new_instance.execute(
                model, 'load', load_fields, batch)
            loaded_data['ids'].extend(res['ids'] or [])
            loaded_data['messages'].extend(res['messages'] or [])
            if res['messages']:
                _logger.error('batch %s, %s', group, batchs)
                for msg in res['messages']:
                    _logger.error(msg)
                    _logger.error(batch[msg['record']])

            if not res.get('ids', False):
                self.write_errors(model, load_fields, batch)
        return loaded_data

    def export(self, model, ids, export_fields):
        data = export_data(
            registry=self.legacy, model=model, ids=ids, header=export_fields,
            max_connection=self.max_connection, batch_size=self.batch_size)

        if not data:
            self.write_errors('export.' + model, ids, [])
            _logger.error('Values were not exported')
        return data

    def export_data(self, model, ids, export_fields):
        export_data_batchs, batchs = self.chunks(ids)
        exported_data = []
        for (group, batch) in enumerate(export_data_batchs, 1):
            _logger.debug("Group %s-%s", group, batchs)
            res = self.legacy.execute(
                model, 'export_data', batch, export_fields)
            exported_data.extend(res['datas'] or [])
            """
            if not res.get('ids', False):
                self.write_errors(model, load_fields, batch)
            """
        return exported_data

    def chunks(self, values):
        """Split a list into a n sublist, where n is the group_size configured
        in the class.
        """
        number = self.group_size
        groups = [values[item:item + number]
                  for item in range(0, len(values), number)]
        group_number = len(groups)
        _logger.info("%s groups of %s", group_number, number)
        return groups, group_number

    def list2dict(self, fields, values):
        data = dict()
        for (index, _item) in enumerate(fields):
            data.update({fields[index]: values[index]})
        return data

    def write_errors(self, model, header, records):
        """ write the list of records that were not
        imported for any error while importing. This way the user will be
        able to fix the error and re imported without mapping again.
        """
        with open(model + '.csv', 'a', newline='') as csvfile:
            wr = csv.writer(csvfile)
            wr.writerow(header)
            wr.writerows(records)

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

    def load_csv(self, csvfile):
        """ receive a csvfile with already prepare and mapped record and try to
        re load into instance.
        """
        with open(csvfile, 'r') as csvfilefile:
            rd = csv.reader(csvfilefile)
            data = list(rd)

        model = csvfile.replace('.csv', '').replace('import.', '')
        self.load(model, data[0], data[1:])

    def get_recoreds_to_update(self, model):
        model_data = self.new_instance.env['ir.model.data']
        to_update = model_data.search([
            ('module', '=', '__export__'), ('model', '=', model)])
        res = model_data.browse(to_update)
        ids = [
            self.legacy.env.ref('.'.join([item.module, item.name]))
            for item in res]
        return ids
