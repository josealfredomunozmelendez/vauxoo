# coding: utf-8
from odoo import models, api
import werkzeug


def urlplus(url, params):
    return werkzeug.Href(url)(params or None)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def google_map_img(self, zoom=8, width=298, height=298):
        partner = self
        params = {
            'center': '%s, %s %s, %s' % (
                partner.street or '',
                partner.city or '',
                partner.zip or '',
                partner.country_id and partner.country_id.name_get()[0][1] or ''),  # noqa
            'size': "%sx%s" % (height, width),
            'zoom': zoom,
            'sensor': 'false',
        }
        return urlplus('//maps.googleapis.com/maps/api/staticmap', params)
