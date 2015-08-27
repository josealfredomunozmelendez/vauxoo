# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class ResPartner(osv.Model):
    _inherit = "res.partner"
    _columns = {
        'certificate_code': fields.char(
            'Certification Cupon',
            groups='ctp_training_tools.certificate_manager',
            help="One time we sold a CTP training "
            "user should be certificated, this "
            "number is sent manually by email from "
            "the Account Manager in OpenERP SA it is "
            "used by the email template to sent as "
            "the conclusion part of the training."),
    }
