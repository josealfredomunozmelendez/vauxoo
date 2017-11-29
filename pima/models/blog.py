# coding: utf-8
from odoo import models, fields


class BlogPost(models.Model):
    _inherit = "blog.post"

    author_avatar_big = fields.Binary(
        related='author_id.image', string="Avatar big")
