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
    "version" : "1.0",
    "depends" : [
        #new modules
        "project_followers_rule",
        "hr_recruitment",
        "hr_evaluation",
        "account_asset",
        "account_budget",
        "account_followup",
        "account_invoice_number",
        "analytic_contract_hr_expense",
        "base_import",
        "contract_enterprise_openerp",
        "email_template_followers",
        "event_sale",
        "expired_task_information",
        "forward_mail",
        "google_docs",
        "hr_contract",
        "hr_expense_replenishment_tax",
        "hr_payslip_paid",
        "ifrs_report",
        "l10n_mx_cities",
        "l10n_mx_facturae_pac_sf",
        "l10n_mx_facturae_pac_finkok",         #Added module of  finkok pac for signed with it invoices and payroll.  Task #1886
        "l10n_mx_payroll_base",                #This module install all about  mexican payroll.  Task #1886
        "l10n_mx_validate_xml_sat",            #This module install a wizard for validate XML signed in SAT  Task #1886
        "lunch",
        "mass_editing",
        "mrp_jit",
        "multi_company",
        "network",
        "note_pad",
        "payroll_amount_residual",
        "portal_project_issue",
        "portal_sale",
        "portal_stock",
        "project_conf",
        "project_btree",
        "project_gtd",
        "project_issue_sheet",
        "project_long_term",
        "project_task_domain",
        "purchase_analytic_plans",
        "sale_multicompany_report",
        "sale_order_report",
        "sale_order_vauxoo_report_webkit",       # This depends is add for install sale order report webkit for Vauxoo Company  Task #1776
        "sync_youtube",
        "user_story",
        "vauxoo_doc",
        "warning",
        "web_allow_custom_root",
        "web_analytics",
        "web_calendar",
        "web_diagram",
        "web_export_view",
        "web_gantt",
        "web_graph",
        "web_nocreatedb",
        "web_tests",
        "web_view_editor",
        "www_vauxoo_com",
        "sale_order_vauxoo_report_webkit",
        "sale_order_copy_line",
        "sale_order_line_seq",
            ],
    "author" : "Vauxoo",
    "description" : """
Install all apps needed to comply with Vauxoo instance
======================================================


                    """,
    "website" : "http://www.vauxoo.com",
    "category" : "Localization/Application",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "test" : [],
    "images" : [],
    "auto_install": False,
    "application": True,
    "installable": True,
}
