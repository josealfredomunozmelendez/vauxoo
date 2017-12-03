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
    "version": "11.0.2.0.2",
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

        # Product
        "product_cost_usd",
    ],
    "data": [
        # Website stuff (A file per page)

        # Main Configuration
        "data/res_config_settings.yml",
        # "data/website_settings.yml",
        # "data/apps.xml",

        # Data
        # 'data/res_currency.xml',
        # 'data/company.xml',
        # 'data/website.xml',
        # 'data/project_tags.xml',
        # "data/ir_actions_server.xml",
        # "data/base_automation.xml",
        # "data/hr_timesheet_invoice_data.xml",
        # "data/product.xml",
        # "data/project.xml",
        # "data/project_task_estimation.xml",
        # "data/jobs.xml",
        # "data/blog.xml",

        # Security
        "security/ir_rule.xml",
        "security/res_groups.xml",
        "security/res_users.xml",
        # "security/ir.model.access.csv",

        # Views
        # Backend stuff (A file per app)
        # "views/helpdesk.xml",
        # "views/project.xml",
        # "views/account_analytic_line_view.xml",
        # "views/hr_timesheet_view.xml",
        # "views/hr_employee_view.xml",
        # "views/account_budget_view.xml",
        # "views/menu.xml",
        # 'views/sale_view.xml',
        #
        # # Reports
        # "report/layout.xml",
        # "report/timesheet_template.xml",
        # 'report/sale_report_templates.xml',
        #
        # # Wizards (One Per Wizard)
        # "wizard/employee_user_view.xml",
        #
        # # Email templates
        # "data/website_quotation_template.xml",
        # "data/email_templates.xml",
        #
        # # Stages Data
        # "data/project_task_stages.xml",
        # "data/sales.xml",
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
