# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo (Formely OpenERP), Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyleft (Cl) 2008-2021 Vauxoo, C.A. (<http://vauxoo.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{   "name" : "Odoo Vauxoo Instance",
    "author" : "Vauxoo",
    "summary": "All the necesary modules to auto install our instance.",
    "description" : """
Install all apps needed to comply with Vauxoo instance
======================================================

TODO: Document all the references (read www_vauxoo_com module as an example)
                    """,
    "website" : "http://www.vauxoo.com",
    "category" : "Vauxoo",
    "version" : "2.0",
    "depends" : [
        # ERP modules (here nothing with website)
        "project_followers_rule",
        "hr_recruitment",
        "hr_evaluation",
        "account_asset",
        "account_budget",
        "account_followup",
        "account_invoice_number",
        "analytic_contract_hr_expense",
        "email_template_followers",
        "expired_task_information",
        "forward_mail",
        "google_drive",
        "google_account",
        "hr_contract",
        "hr_expense_replenishment_tax",
        "hr_payslip_paid",
        "ifrs_report",
        "l10n_mx_cities",
        "l10n_mx_facturae_pac_sf",
        "l10n_mx_facturae_pac_finkok",         #Added module of  finkok pac for signed with it invoices and payroll.  Task #1886
        "l10n_mx_payroll_base",                #This module install all about  mexican payroll.  Task #1886
        "l10n_mx_validate_xml_sat",            #This module install a wizard for validate XML signed in SAT  Task #1886
        "procurement_jit",
        "multi_company",
        "network",
        "note_pad",
        "payroll_amount_residual",
        "portal_project_issue",
        "portal_sale",
        "portal_stock",
        "project_conf",
        "project_btree",
        "project_issue_sheet",
        "project_task_domain",
        "purchase_analytic_plans",
        "sale_multicompany_report",
        "sale_order_report",
        "sync_youtube",
        "user_story",
        "warning",
        "sale_order_copy_line",
        ],
    "data" : [],
    "demo" : [],
    "test" : [
        # Only our tests (the custom ones)
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
