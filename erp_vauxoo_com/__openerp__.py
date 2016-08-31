# coding: utf-8
{
    "name": "Odoo Vauxoo ERP Instance",
    "author": "Vauxoo",
    "summary": "All the necesary modules to auto install our instance.",
    "website": "http://www.vauxoo.com",
    "license": "AGPL-3",
    "category": "Vauxoo",
    "version": "2.0",
    "depends": [
        # ERP modules (here nothing with website)
        # "project_followers_rule",
        "account_asset",
        "account_budget",
        # "ifrs_report",
        # "account_followup",
        # "account_invoice_number",
        # "account_reconcile_grouping",
        # "account_smart_unreconcile",
        # "analytic_contract_hr_expense",
        # Human Resourse section, try to avoid double dependency.
        'hr_payroll_multicompany',
        # "l10n_mx_payroll_base",  # Review task 1886
        # "hr_expense_replenishment_tax",
        # "hr_payslip_paid",
        # "hr_evaluation",
        # "l10n_mx_cities",
        # "l10n_mx_facturae_pac_sf",
        # "auth_crypt",
        # "hr_timesheet_reports",
        # "vauxoo_sale_reports",
        # Added module of finkok pac for signed with it invoices and payroll.
        # Task #1886
        # "l10n_mx_facturae_pac_finkok",
        # This module install all about  mexican payroll.  Task #1886
        # This module install a wizard for validate XML signed in SAT  Task
        # #1886
        # "l10n_mx_validate_xml_sat",
        # "l10n_mx_diot_report",
        # "l10n_mx_facturae_report_zebra",
        # "account_financial_report",
        # "aging_due_report",
        # "procurement_jit",
        "inter_company_rules",
        # "expired_task_information", In favor of Forcast I think.
        # "forward_mail",
        # "google_drive",
        # "google_account",
        # "payroll_amount_residual",
        # Project Section.
        "project_issue_sheet",
        'project_timesheet_synchro',  # Enable the sync of timesheet.
        "project_issue_management",
        # "project_issue_conf",
        # "user_story_scrum",
        "warning",
        # "sale_order_copy_line",  [MIG] vauxoo/addons-vauxoo#722
        # "web_export_view", Tool used but better for next iteration
        # Portal (not website) modules
        # "portal_user_story",
        "crm_partner_assign",  # NECESARY BUT NOT SINC BEGINING.
        # Technical tools.
        # 'send_author_mail',
        # 'mass_editing',
        # 'account_move_filters',
        oml,
    ],
    "data": [
        "security/res_groups.xml",
        # "data/set_configuration.yml",
    ],
    "demo": [],
    "test": [
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
