# coding: utf-8
import time
import datetime
from email import utils
from odoo import models, fields, api


class BlogPost(models.Model):
    _inherit = 'blog.post'

    @api.multi
    def _get_date(self):
        posts = self
        for post in posts:
            date_obj = time.strptime(post.write_date, "%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.fromtimestamp(time.mktime(date_obj))
            write_tuple = dt.timetuple()
            timestamp = time.mktime(write_tuple)
            post.date_rfc2822 = utils.formatdate(timestamp)

    date_rfc2822 = fields.Char(
        compute=_get_date,
        string="Date RFC-2822")
