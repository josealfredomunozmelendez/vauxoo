# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo Web Login Screen
#    Copyright (C) 2016- XUBI.ME (http://www.xubi.me)
#    @author binhnguyenxuan (https://www.linkedin.com/in/binh-nguyen-xuan-46556279)
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
##############################################################################
import ast

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home

import datetime
import pytz


class Home(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        # import pdb; pdb.set_trace()
        param_obj = request.env['ir.config_parameter']
        request.params['disable_footer'] = ast.literal_eval(param_obj.get_param('login_form_disable_footer')) or False
        request.params['disable_database_manager'] = ast.literal_eval(param_obj.get_param('login_form_disable_database_manager')) or False
        background_src = param_obj.get_param('login_form_background_default') or ''
        request.params['background_src'] = background_src
        change_background = ast.literal_eval(param_obj.get_param('login_form_change_background_by_hour')) or False
        if not change_background:
            return super(Home, self).web_login(redirect, **kw)
        config_login_timezone = param_obj.get_param('login_form_change_background_timezone')
        tz = config_login_timezone and pytz.timezone(config_login_timezone) or pytz.utc
        current_hour = datetime.datetime.now(tz=tz).hour
        if 3 > current_hour >= 0 or 24 > current_hour >= 18:
            background_src = param_obj.get_param('login_form_background_night') or ''
        elif 7 > current_hour >= 3:
            background_src = param_obj.get_param('login_form_background_dawn') or ''
        elif 16 > current_hour >= 7:
            background_src = param_obj.get_param('login_form_background_day') or ''
        else:
            background_src = param_obj.get_param('login_form_background_dusk') or ''
        request.params['background_src'] = background_src
        return super(Home, self).web_login(redirect, **kw)
