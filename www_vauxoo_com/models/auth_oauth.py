from openerp import models, fields


class auth_oauth_provider(models.Model):
    _inherit = "auth.oauth.provider"
    btn_class = fields.Char('Btn Class')
