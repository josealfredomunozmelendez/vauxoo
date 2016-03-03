# coding: utf-8
# © 2016 Vauxoo
#   Coded by: lescobar@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Runbot Configurator",
    "summary": "This module install and configure runbot with basic data.",
    "version": "8.0.1.0.0",
    "category": "runbot",
    "website": "https://www.vauxoo.com",
    "author": "Vauxoo, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "runbot",
        "runbot_travis2docker",
        "runbot_send_email",
    ],
    "data": [
        "runbot_vauxoo_com_data.xml",
    ],
    "demo": [
    ],
    "application": False,
    "installable": True,
}
