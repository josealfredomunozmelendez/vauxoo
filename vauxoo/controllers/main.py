# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Pricing(http.Controller):

    @http.route('/pricing', type='http', auth='public', website=True)
    def pricing(self, **post):
        return request.render('vauxoo.apps_pricing', {})
