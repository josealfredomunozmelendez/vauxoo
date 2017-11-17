# -*- coding: utf-8 -*-

import logging

from collections import defaultdict
from odoo.tools import pycompat
from odoo import models, api, tools, SUPERUSER_ID, _
from odoo.exceptions import MissingError, UserError
from odoo.models import LOG_ACCESS_COLUMNS, MAGIC_COLUMNS  # noqa  pylint: disable=unused-import
models.LOG_ACCESS_COLUMNS = []
models.MAGIC_COLUMNS = ['id'] + models.LOG_ACCESS_COLUMNS


_logger = logging.getLogger(__name__)


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context(
        'self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        magic_active, magic_user = self._get_magic()
        # User id which will made the migration
        if self._uid in [SUPERUSER_ID,
                         int(magic_user)] and magic_active == 'True':
            return True
        return super(IrModelAccess, self).check(model, mode, raise_exception)


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_magic(self):
        self._cr.execute(
            "SELECT value from ir_config_parameter where key='magic_uid'")
        magic_user = SUPERUSER_ID
        res = self._cr.fetchone()
        if res:
            magic_user = res[0]
        self._cr.execute(
            "SELECT value from ir_config_parameter where key='magic_active'")
        magic_active = False
        res = self._cr.fetchone()
        if res:
            magic_active = res[0]
        return magic_active, magic_user

    @api.multi
    def check_access_rule(self, operation):
        magic_active, magic_user = self._get_magic()
        # User id which will made the migration
        if self._uid in [SUPERUSER_ID,
                         int(magic_user)] and magic_active == 'True':
            return
        return super(Base, self).check_access_rule(operation)

    @api.multi
    def write(self, vals):
        magic_active = self._get_magic()[0]
        if magic_active != 'True':
            return super(Base, self).write(vals)
        if not self:
            return True

        self._check_concurrency()
        self.check_access_rights('write')

        # No user-driven update of these columns
        pop_fields = ['parent_left', 'parent_right']
        if self._log_access:
            pop_fields.extend(models.MAGIC_COLUMNS)
        for field in pop_fields:
            vals.pop(field, None)

        # split up fields into old-style and pure new-style ones
        old_vals, new_vals, unknown = {}, {}, []
        for key, val in vals.items():
            field = self._fields.get(key)
            if field:
                if field.store or field.inherited:
                    old_vals[key] = val
                if field.inverse and not field.inherited:
                    new_vals[key] = val
            else:
                unknown.append(key)

        if unknown:
            _logger.warning("%s.write() with unknown fields: %s", self._name, ', '.join(sorted(unknown)))  # noqa

        protected_fields = [self._fields[n] for n in new_vals]
        with self.env.protecting(protected_fields, self):
            # write old-style fields with (low-level) method _write
            if old_vals:
                self._write(old_vals)

            if new_vals:
                # put the values of pure new-style fields into cache, and inverse them  # noqa
                self.modified(set(new_vals) - set(old_vals))
                for record in self:
                    record._cache.update(record._convert_to_cache(new_vals, update=True))  # noqa
                for key in new_vals:
                    self._fields[key].determine_inverse(self)
                self.modified(set(new_vals) - set(old_vals))
                # check Python constraints for inversed fields
                self._validate_fields(set(new_vals) - set(old_vals))
                # recompute new-style fields
                if self.env.recompute and self._context.get('recompute', True):
                    self.recompute()

        return True

    @api.multi
    def _write(self, vals):
        magic_active = self._get_magic()[0]
        if magic_active != 'True':
            return super(Base, self)._write(vals)
        # low-level implementation of write()
        if not self:
            return True
        self.check_field_access_rights('write', list(vals))

        cr = self._cr

        # for recomputing new-style fields
        extra_fields = ['write_date', 'write_uid'] if self._log_access else []
        self.modified(list(vals) + extra_fields)

        # for updating parent_left, parent_right
        parents_changed = []
        if self._parent_store and (self._parent_name in vals) and \
                not self._context.get('defer_parent_store_computation'):
            # The parent_left/right computation may take up to 5 seconds. No
            # need to recompute the values if the parent is the same.
            #
            # Note: to respect parent_order, nodes must be processed in
            # order, so ``parents_changed`` must be ordered properly.
            parent_val = vals[self._parent_name]
            if parent_val:
                query = """
                SELECT id FROM %s WHERE id IN %%s AND
                (%s != %%s OR %s IS NULL) ORDER BY %s""" % \
                                (self._table, self._parent_name, self._parent_name, self._parent_order)  # noqa
                cr.execute(query, (tuple(self.ids), parent_val))
            else:
                query = """
                SELECT id FROM %s WHERE id IN %%s AND
                (%s IS NOT NULL) ORDER BY %s""" % \
                                (self._table, self._parent_name, self._parent_order)  # noqa
                cr.execute(query, (tuple(self.ids),))
            parents_changed = [x[0] for x in cr.fetchall()]

        updates = []            # list of (column, expr) or (column, pattern, value)  # noqa
        upd_todo = []           # list of column names to set explicitly
        updend = []             # list of possibly inherited field names
        direct = []             # list of direcly updated columns
        has_trans = self.env.lang and self.env.lang != 'en_US'
        single_lang = len(self.env['res.lang'].get_installed()) <= 1
        for name, val in vals.items():
            field = self._fields[name]
            if field and field.deprecated:
                _logger.warning('Field %s.%s is deprecated: %s', self._name, name, field.deprecated)  # noqa
            if field.store:
                if hasattr(field, 'selection') and val:
                    self._check_selection_field_value(name, val)
                if field.column_type:
                    if single_lang or not (has_trans and field.translate is True):  # noqa
                        # val is not a translation: update the table
                        val = field.convert_to_column(val, self, vals)
                        updates.append((name, field.column_format, val))
                    direct.append(name)
                else:
                    upd_todo.append(name)
            else:
                updend.append(name)

        # THIS IS THE MAIN PROPUSE OF THIS UGLY PATCH SINCE THERE NO OTHER WAY
        # TO AVOID THIS SECTION
        # if self._log_access:
        #     updates.append(('write_uid', '%s', self._uid))
        #     updates.append(('write_date', "(now() at time zone 'UTC')"))
        #     direct.append('write_uid')
        #     direct.append('write_date')

        if updates:
            self.check_access_rule('write')
            query = 'UPDATE "%s" SET %s WHERE id IN %%s' % (
                self._table, ','.join('"%s"=%s' % (u[0], u[1]) for u in updates),  # noqa
            )
            params = tuple(u[2] for u in updates if len(u) > 2)
            for sub_ids in cr.split_for_in_conditions(set(self.ids)):
                cr.execute(query, params + (sub_ids,))
                if cr.rowcount != len(sub_ids):
                    raise MissingError(_('One of the records you are trying to modify has already been deleted (Document type: %s).') % self._description)  # noqa

            # TODO: optimize
            for name in direct:
                field = self._fields[name]
                if callable(field.translate):
                    # The source value of a field has been modified,
                    # synchronize translated terms when possible.
                    self.env['ir.translation']._sync_terms_translations(self._fields[name], self)  # noqa

                elif has_trans and field.translate:
                    # The translated value of a field has been modified.
                    src_trans = self.read([name])[0][name]
                    if not src_trans:
                        # Insert value to DB
                        src_trans = vals[name]
                        self.with_context(lang=None).write({name: src_trans})
                    val = field.convert_to_column(vals[name], self, vals)
                    tname = "%s,%s" % (self._name, name)
                    self.env['ir.translation']._set_ids(
                        tname, 'model', self.env.lang, self.ids, val, src_trans)  # noqa

        # invalidate and mark new-style fields to recompute; do this before
        # setting other fields, because it can require the value of computed
        # fields, e.g., a one2many checking constraints on records
        self.modified(direct)

        # defaults in context must be removed when call a one2many or many2many
        rel_context = {key: val
                       for key, val in self._context.items()
                       if not key.startswith('default_')}

        # call the 'write' method of fields which are not columns
        for name in upd_todo:
            field = self._fields[name]
            field.write(self.with_context(rel_context), vals[name])

        # for recomputing new-style fields
        self.modified(upd_todo)

        # write inherited fields on the corresponding parent records
        unknown_fields = set(updend)
        for parent_model, parent_field in self._inherits.items():
            parent_ids = []
            for sub_ids in cr.split_for_in_conditions(self.ids):
                query = "SELECT DISTINCT %s FROM %s WHERE id IN %%s" % (parent_field, self._table)  # noqa
                cr.execute(query, (sub_ids,))
                parent_ids.extend([row[0] for row in cr.fetchall()])

            parent_vals = {}
            for name in updend:
                field = self._fields[name]
                if field.inherited and field.related[0] == parent_field:
                    parent_vals[name] = vals[name]
                    unknown_fields.discard(name)

            if parent_vals:
                self.env[parent_model].browse(parent_ids).write(parent_vals)

        if unknown_fields:
            _logger.warning('No such field(s) in model %s: %s.', self._name, ', '.join(unknown_fields))  # noqa

        # check Python constraints
        self._validate_fields(vals)

        # TODO: use _order to set dest at the right position and not first node of parent  # noqa
        # We can't defer parent_store computation because the stored function
        # fields that are computer may refer (directly or indirectly) to
        # parent_left/right (via a child_of domain)
        if parents_changed:
            if self.pool._init:
                self.pool._init_parent[self._name] = True
            else:
                parent_val = vals[self._parent_name]
                if parent_val:
                    clause, params = '%s=%%s' % self._parent_name, (parent_val,)  # noqa
                else:
                    clause, params = '%s IS NULL' % self._parent_name, ()

                for id in parents_changed:  # pylint: disable=redefined-builtin
                    # determine old parent_left, parent_right of current record
                    cr.execute('SELECT parent_left, parent_right FROM %s WHERE id=%%s' % self._table, (id,))  # noqa
                    pleft0, pright0 = cr.fetchone()
                    width = pright0 - pleft0 + 1

                    # determine new parent_left of current record; it comes
                    # right after the parent_right of its closest left sibling
                    # (this CANNOT be fetched outside the loop, as it needs to
                    # be refreshed after each update, in case several nodes are
                    # sequentially inserted one next to the other)
                    pleft1 = None
                    cr.execute(
                        '''SELECT id, parent_right FROM %s WHERE
                        %s ORDER BY %s''' %
                               (self._table, clause, self._parent_order), params)  # noqa
                    for (sibling_id, sibling_parent_right) in cr.fetchall():
                        if sibling_id == id:
                            break
                        pleft1 = (sibling_parent_right or 0) + 1
                    if not pleft1:
                        # the current record is the first node of the parent
                        if not parent_val:
                            pleft1 = 0          # the first node starts at 0
                        else:
                            cr.execute('SELECT parent_left FROM %s WHERE id=%%s' % self._table, (parent_val,))  # noqa
                            pleft1 = cr.fetchone()[0] + 1

                    if pleft0 < pleft1 <= pright0:
                        raise UserError(_('Recursivity Detected.'))

                    # make some room for parent_left and parent_right at the new position  # noqa
                    cr.execute('UPDATE %s SET parent_left=parent_left+%%s WHERE %%s<=parent_left' % self._table, (width, pleft1))  # noqa
                    cr.execute('UPDATE %s SET parent_right=parent_right+%%s WHERE %%s<=parent_right' % self._table, (width, pleft1))  # noqa
                    # slide the subtree of the current record to its new position  # noqa
                    if pleft0 < pleft1:
                        cr.execute('''UPDATE %s SET parent_left=parent_left+%%s, parent_right=parent_right+%%s
                                      WHERE %%s<=parent_left AND parent_left<%%s''' % self._table,  # noqa
                                   (pleft1 - pleft0, pleft1 - pleft0, pleft0, pright0))  # noqa
                    else:
                        cr.execute('''UPDATE %s SET parent_left=parent_left-%%s, parent_right=parent_right-%%s
                                      WHERE %%s<=parent_left AND parent_left<%%s''' % self._table,  # noqa
                                   (pleft0 - pleft1 + width, pleft0 - pleft1 + width, pleft0 + width, pright0 + width))  # noqa

                self.invalidate_cache(['parent_left', 'parent_right'])

        # recompute new-style fields
        if self.env.recompute and self._context.get('recompute', True):
            self.recompute()

        return True

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        magic_active = self._get_magic()[0]
        if magic_active != 'True':
            return super(Base, self).create(vals)
        self.check_access_rights('create')

        # add missing defaults, and drop fields that may not be set by user
        vals = self._add_missing_default_values(vals)
        pop_fields = ['parent_left', 'parent_right']
        if self._log_access:
            pop_fields.extend(models.MAGIC_COLUMNS)
        for field in pop_fields:
            vals.pop(field, None)

        # split up fields into old-style and pure new-style ones
        old_vals, new_vals, unknown = {}, {}, []
        for key, val in vals.items():
            field = self._fields.get(key)
            if field:
                if field.store or field.inherited:
                    old_vals[key] = val
                if field.inverse and not field.inherited:
                    new_vals[key] = val
            else:
                unknown.append(key)

        if unknown:
            _logger.warning("%s.create() includes unknown fields: %s", self._name, ', '.join(sorted(unknown)))  # noqa

        # create record with old-style fields
        record = self.browse(self._create(old_vals))

        protected_fields = [self._fields[n] for n in new_vals]
        with self.env.protecting(protected_fields, record):
            # put the values of pure new-style fields into cache, and inverse them  # noqa
            record.modified(set(new_vals) - set(old_vals))
            record._cache.update(record._convert_to_cache(new_vals))
            for key in new_vals:
                self._fields[key].determine_inverse(record)
            record.modified(set(new_vals) - set(old_vals))
            # check Python constraints for inversed fields
            record._validate_fields(set(new_vals) - set(old_vals))
            # recompute new-style fields
            if self.env.recompute and self._context.get('recompute', True):
                self.recompute()

        return record

    @api.model
    def _create(self, vals):
        magic_active = self._get_magic()[0]
        if magic_active != 'True':
            return super(Base, self)._create(vals)
        # data of parent records to create or update, by model
        tocreate = {
            parent_model: {'id': vals.pop(parent_field, None)}
            for parent_model, parent_field in self._inherits.items()
        }

        # list of column assignments defined as tuples like:
        #   (column_name, format_string, column_value)
        #   (column_name, sql_formula)
        # Those tuples will be used by the string formatting for the INSERT
        # statement below.
        updates = [
            ('id', "nextval('%s')" % self._sequence),
        ]

        upd_todo = []
        unknown_fields = []
        protected_fields = []
        for name, val in list(vals.items()):
            field = self._fields.get(name)
            if not field:
                unknown_fields.append(name)
                del vals[name]
            elif field.inherited:
                tocreate[field.related_field.model_name][name] = val
                del vals[name]
            elif not field.store:
                del vals[name]
            elif field.inverse:
                protected_fields.append(field)
        if unknown_fields:
            _logger.warning('No such field(s) in model %s: %s.', self._name, ', '.join(unknown_fields))  # noqa

        # create or update parent records
        for parent_model, parent_vals in tocreate.items():
            parent_id = parent_vals.pop('id')
            if not parent_id:
                parent_id = self.env[parent_model].create(parent_vals).id
            else:
                self.env[parent_model].browse(parent_id).write(parent_vals)
            vals[self._inherits[parent_model]] = parent_id

        # set boolean fields to False by default (to make search more powerful)
        for name, field in self._fields.items():
            if field.type == 'boolean' and field.store and name not in vals:
                vals[name] = False

        # determine SQL values
        self = self.browse()
        for name, val in vals.items():
            field = self._fields[name]
            if field.store and field.column_type:
                column_val = field.convert_to_column(val, self, vals)
                updates.append((name, field.column_format, column_val))
            else:
                upd_todo.append(name)

            if hasattr(field, 'selection') and val:
                self._check_selection_field_value(name, val)

        # THIS IS THE MAIN PROPUSE OF THIS UGLY PATCH SINCE THERE NO OTHER WAY
        # TO AVOID THIS SECTION
        # if self._log_access:
        #     updates.append(('create_uid', '%s', self._uid))
        #     updates.append(('write_uid', '%s', self._uid))
        #     updates.append(('create_date', "(now() at time zone 'UTC')"))
        #     updates.append(('write_date', "(now() at time zone 'UTC')"))

        # insert a row for this record
        cr = self._cr
        query = """INSERT INTO "%s" (%s) VALUES(%s) RETURNING id""" % (
                self._table,
                ', '.join('"%s"' % u[0] for u in updates),
                ', '.join(u[1] for u in updates),
            )
        cr.execute(query, tuple(u[2] for u in updates if len(u) > 2))

        # from now on, self is the new record
        id_new, = cr.fetchone()
        self = self.browse(id_new)

        if self._parent_store and not self._context.get('defer_parent_store_computation'):  # noqa
            if self.pool._init:
                self.pool._init_parent[self._name] = True
            else:
                parent_val = vals.get(self._parent_name)
                if parent_val:
                    # determine parent_left: it comes right after the
                    # parent_right of its closest left sibling
                    pleft = None
                    cr.execute(
                        """SELECT parent_right FROM %s WHERE
                        %s=%%s ORDER BY %s""" %
                                    (self._table, self._parent_name, self._parent_order),  # noqa
                               (parent_val,))
                    for (pright,) in cr.fetchall():
                        if not pright:
                            break
                        pleft = pright + 1
                    if not pleft:
                        # this is the leftmost child of its parent
                        cr.execute("SELECT parent_left FROM %s WHERE id=%%s" % self._table, (parent_val,))  # noqa
                        pleft = cr.fetchone()[0] + 1
                else:
                    # determine parent_left: it comes after all top-level parent_right  # noqa
                    cr.execute("SELECT MAX(parent_right) FROM %s" % self._table)  # noqa
                    pleft = (cr.fetchone()[0] or 0) + 1

                # make some room for the new node, and insert it in the MPTT
                cr.execute("UPDATE %s SET parent_left=parent_left+2 WHERE parent_left>=%%s" % self._table,  # noqa
                           (pleft,))
                cr.execute("UPDATE %s SET parent_right=parent_right+2 WHERE parent_right>=%%s" % self._table,  # noqa
                           (pleft,))
                cr.execute("UPDATE %s SET parent_left=%%s, parent_right=%%s WHERE id=%%s" % self._table,  # noqa
                           (pleft, pleft + 1, id_new))
                self.invalidate_cache(['parent_left', 'parent_right'])

        with self.env.protecting(protected_fields, self):
            # invalidate and mark new-style fields to recompute; do this before
            # setting other fields, because it can require the value of computed  # noqa
            # fields, e.g., a one2many checking constraints on records
            self.modified(self._fields)

            # defaults in context must be removed when call a one2many or many2many  # noqa
            rel_context = {key: val
                           for key, val in self._context.items()
                           if not key.startswith('default_')}

            # call the 'write' method of fields which are not columns
            for name in sorted(upd_todo, key=lambda name: self._fields[name]._sequence):  # noqa
                field = self._fields[name]
                field.write(self.with_context(rel_context), vals[name], create=True)  # noqa

            # for recomputing new-style fields
            self.modified(upd_todo)

            # check Python constraints
            self._validate_fields(vals)

            if self.env.recompute and self._context.get('recompute', True):
                # recompute new-style fields
                self.recompute()

        self.check_access_rule('create')

        if self.env.lang and self.env.lang != 'en_US':
            # add translations for self.env.lang
            for name, val in vals.items():
                field = self._fields[name]
                if field.store and field.column_type and field.translate is True:  # noqa
                    tname = "%s,%s" % (self._name, name)
                    self.env['ir.translation']._set_ids(tname, 'model', self.env.lang, self.ids, val, val)  # noqa

        return id_new

    @api.model
    def _add_missing_default_values(self, values):
        magic_active = self._get_magic()[0]
        if magic_active != 'True':
            return super(Base, self)._add_missing_default_values(values)
        # avoid overriding inherited values when parent is set
        avoid_models = {
            parent_model
            for parent_model, parent_field in self._inherits.items()
            if parent_field in values
        }

        # compute missing fields
        missing_defaults = {
            name
            for name, field in self._fields.items()
            if name not in values
            if self._log_access and name not in models.MAGIC_COLUMNS
            if not (field.inherited and field.related_field.model_name in avoid_models)  # noqa
        }

        if not missing_defaults:
            return values

        # override defaults with the provided values, never allow the other way around  # noqa
        defaults = self.default_get(list(missing_defaults))
        for name, value in defaults.items():
            if self._fields[name].type == 'many2many' and value and isinstance(value[0], pycompat.integer_types):  # noqa
                # convert a list of ids into a list of commands
                defaults[name] = [(6, 0, value)]
            elif self._fields[name].type == 'one2many' and value and isinstance(value[0], dict):  # noqa
                # convert a list of dicts into a list of commands
                defaults[name] = [(0, 0, x) for x in value]
        defaults.update(values)
        return defaults

    @api.multi
    def get_metadata(self):
        magic_active = self._get_magic()[0]
        if magic_active != 'True':
            return super(Base, self).get_metadata()
        fields = ['id']
        if self._log_access:
            fields += models.LOG_ACCESS_COLUMNS
        quoted_table = '"%s"' % self._table
        fields_str = ",".join('%s.%s' % (quoted_table, field) for field in fields)  # noqa
        query = '''SELECT %s, __imd.noupdate, __imd.module, __imd.name
                   FROM %s LEFT JOIN ir_model_data __imd
                       ON (__imd.model = %%s and __imd.res_id = %s.id)
                   WHERE %s.id IN %%s''' % (fields_str, quoted_table, quoted_table, quoted_table)  # noqa
        self._cr.execute(query, (self._name, tuple(self.ids)))
        res = self._cr.dictfetchall()

        uids = set(r[k] for r in res for k in ['write_uid', 'create_uid'] if r.get(k))  # noqa
        names = dict(self.env['res.users'].browse(uids).name_get())

        for r in res:  # pylint: disable=invalid-name
            for key in r:
                value = r[key] = r[key] or False
                if key in ('write_uid', 'create_uid') and value in names:
                    r[key] = (value, names[value])
            r['xmlid'] = ("%(module)s.%(name)s" % r) if r['name'] else False
            del r['name'], r['module']
        return res

    @api.multi
    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        magic_active = self._get_magic()[0]
        if magic_active != 'True':
            return super(Base, self).copy_data(default)
        # In the old API, this method took a single id and return a dict. When
        # invoked with the new API, it returned a list of dicts.
        self.ensure_one()

        # avoid recursion through already copied records in case of circular relationship  # noqa
        if '__copy_data_seen' not in self._context:
            self = self.with_context(__copy_data_seen=defaultdict(set))
        seen_map = self._context['__copy_data_seen']
        if self.id in seen_map[self._name]:
            return
        seen_map[self._name].add(self.id)

        default = dict(default or [])
        if 'state' not in default and 'state' in self._fields:
            field = self._fields['state']
            if field.default:
                value = field.default(self)
                value = field.convert_to_cache(value, self)
                value = field.convert_to_record(value, self)
                value = field.convert_to_write(value, self)
                default['state'] = value

        # build a black list of fields that should not be copied
        blacklist = set(models.MAGIC_COLUMNS + ['parent_left', 'parent_right'])  # noqa
        whitelist = set(name for name, field in self._fields.items() if not field.inherited)  # noqa

        def blacklist_given_fields(model):
            # blacklist the fields that are given by inheritance
            for parent_model, parent_field in model._inherits.items():
                blacklist.add(parent_field)
                if parent_field in default:
                    # all the fields of 'parent_model' are given by the record:
                    # default[parent_field], except the ones redefined in self
                    blacklist.update(set(self.env[parent_model]._fields) - whitelist)  # noqa
                else:
                    blacklist_given_fields(self.env[parent_model])
            # blacklist deprecated fields
            for name, field in model._fields.items():
                if field.deprecated:
                    blacklist.add(name)

        blacklist_given_fields(self)

        fields_to_copy = {name: field
                          for name, field in self._fields.items()
                          if field.copy and name not in default and name not in blacklist}  # noqa

        for name, field in fields_to_copy.items():
            if field.type == 'one2many':
                # duplicate following the order of the ids because we'll rely on  # noqa
                # it later for copying translations in copy_translation()!
                lines = [rec.copy_data()[0] for rec in self[name].sorted(key='id')]  # noqa
                # the lines are duplicated using the wrong (old) parent, but then  # noqa
                # are reassigned to the correct one thanks to the (0, 0, ...)
                default[name] = [(0, 0, line) for line in lines if line]
            elif field.type == 'many2many':
                default[name] = [(6, 0, self[name].ids)]
            else:
                default[name] = field.convert_to_write(self[name], self)

        return [default]

    # pylint: disable=C0301,C0103
    # pylint: disable=global-at-module-level
    # pylint: disable=too-complex,sql-injection,redefined-builtin
    # pylint: disable=W0404,W0604,W0622,W0611
