# coding: utf-8
from odoo import api, models


class LangConfigSetting(models.TransientModel):

    _name = 'lang.config.settings'

    @api.model
    def load_lang(self, code='es_ES'):

        lang_obj = self.env['res.lang']
        lang = lang_obj.search([('code', '=', code)])

        if not lang:
            lang_obj.load_lang(code)
            lang = lang_obj.search([('code', '=', code)])

        if lang.active:
            websites = self.env["website"].search([])
            self.env['base.language.install'].create({
                "lang": code,
                "website_ids": [(6, 0, [item.id for item in websites])],
            }).lang_install()

            website_conf = self.env["website.config.settings"].search(
                [], limit=1, order="id desc")
            website_conf.write({
                "default_lang_id": lang.id,
                "language_ids": [(4, lang.id)]})
