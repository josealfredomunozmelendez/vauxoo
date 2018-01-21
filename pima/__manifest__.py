# coding: utf-8
{
    "name": "Pima ERP Instance",
    "author": "PIMA",
    "summary": """
    All the necessary modules to auto install our service instance
    """,
    "website": "http://www.pima.com",
    "license": "LGPL-3",
    "category": "PIMA",
    "version": "11.0.1.0.0",
    "depends": [
        # Account section
        "account_accountant",
        "account_budget",
        "account_reports_followup",
        "account_online_sync",
        "account_voucher",
        "account_analytic_default",
        "account_accountant",
        "account_payment",

        # Project Section.
        "purchase_requisition",
        "project_forecast",
        "helpdesk",

        # Human resources
        "hr_expense",

        # Localizations
        "l10n_mx_edi",
        "l10n_mx_reports",

        # Website modules
        "login",

        # Sales
        "mrp",
        "crm",
        "sale_management",
        "sale_margin",
        "sale_timesheet",
        "sale_expense",
        "sale_stock",
        "sale_subscription",

        # Tools
        "document",
        "base_automation",
        "inter_company_rules",
        'auth_oauth',
        "mass_editing",
        "board",
        "contacts",
        "google_account",
    ],
    "data": [
        # Main Configuration
        "data/res_config_settings.yml",
        # Data
        'data/res_currency.xml',
        'data/company.xml',
        'data/project_tags.xml',
        "data/hr_timesheet_invoice_data.xml",
        "data/product.xml",
        "data/project_task_estimation.xml",
        # Security
        "security/ir_rule.xml",
        "security/res_users.xml",
        "security/ir.model.access.csv",
        # Views
        "views/project.xml",
        "views/account_analytic_line_view.xml",
        "views/account_budget_view.xml",
        "views/menu.xml",
        # # Reports
        "report/layout.xml",
        "report/timesheet_template.xml",
        'report/sale_report_templates.xml',
        # # Wizards (One Per Wizard)
        "wizard/employee_user_view.xml",
        # # Stages Data
        "data/sales.xml",
    ],
    "demo": [
    ],
    "test": [
    ],
    "qweb": ['static/src/xml/*.xml'],
    "auto_install": False,
    "application": True,
    "installable": True,
}
