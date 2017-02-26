# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo Web Login Screen
#    Copyright (C) 2016- XUBI.ME (http://www.xubi.me)
#    @author binhnguyenxuan
#    (https://www.linkedin.com/in/binh-nguyen-xuan-46556279)

from ast import literal_eval

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home

import datetime
import pytz
from pytz import timezone


class LoginHome(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        param = request.env['ir.config_parameter'].sudo()
        get_param = param.get_param
        lfdf = literal_eval(get_param('login_form_disable_footer'))
        print '-'*50
        request.params['disable_footer'] = lfdf or False
        lfddm = literal_eval(get_param('login_form_disable_database_manager'))
        request.params['disable_database_manager'] = lfddm or False
        background = get_param('login_form_background_default') or ''
        request.params['background_src'] = background
        change = literal_eval(
            get_param('login_form_change_background_by_hour') or '')
        if not change:
            return super(LoginHome, self).web_login(redirect, **kw)
        clt = get_param('login_form_change_background_timezone')
        tz = timezone(clt) if clt else pytz.utc
        current_hour = datetime.datetime.now(tz=tz).hour
        if 3 > current_hour >= 0 or 24 > current_hour >= 18:
            background = get_param('login_form_background_night') or ''
        elif 7 > current_hour >= 3:
            background = get_param('login_form_background_dawn') or ''
        elif 16 > current_hour >= 7:
            background = get_param('login_form_background_day') or ''
        else:
            background = get_param('login_form_background_dusk') or ''
        request.params['background_src'] = background
        return super(LoginHome, self).web_login(redirect, **kw)
