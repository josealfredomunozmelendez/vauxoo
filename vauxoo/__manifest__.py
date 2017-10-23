# coding: utf-8
{
    "name": "Vauxoo ERP Instance",
    "author": "Vauxoo",
    "summary": """
    All the necessary modules to auto install our service instance
    """,
    "website": "http://www.vauxoo.com",
    "license": "LGPL-3",
    "category": "Vauxoo",
    "version": "10.0.2.0.1",
    "depends": [
        # Account section
        "account_asset",
        "account_budget",
        "account_reports_followup",
        "account_online_sync",
        "account_cancel",
        "account_test",
        "account_voucher",
        "account_analytic_default",

        # Project Section.
        'project_timesheet_synchro',
        "project_forecast",
        "rating_project",

        # Human resources
        "hr_expense",
        "hr_appraisal",
        "hr_payroll",
        "hr_attendance",

        # Localizations
        "l10n_mx_edi",
        "l10n_mx_reports",

        # Website modules
        "theme_vauxoo",
        'website_crm',
        "website_event",
        "website_hr_recruitment",
        "website_sale_digital",
        "website_quote",
        "website_forum_doc",
        "website_blog",
        "website_customer",
        "website_slides",
        "sale_subscription",
        "website_links",
        "website_hr",
        "website_helpdesk_form",
        "website_sale_options",
        "website_sale_coupon",
        "website_livechat",
        "website_twitter",
        "payment_paypal",
        "marketing_automation",
        "login",

        # Sales
        "sale_margin",

        # Tools
        "document",
        "base_automation",
        "inter_company_rules",
        'auth_oauth',
        "mass_editing",
        "board",
        "contacts",

        # Product
        "product_cost_usd",
    ],
    "data": [
        # Website stuff (A file per page)
        "views/pages/assets.xml",
        "views/pages/image_library.xml",
        "views/pages/blog.xml",
        "views/pages/homepage.xml",
        "views/pages/about.xml",
        "views/pages/careers.xml",
        "views/pages/erp.xml",
        "views/pages/shop.xml",
        "views/pages/contactus.xml",
        "views/pages/job_detail_template.xml",
        "views/pages/apps.xml",

        # Main Configuration
        "data/res_config_settings.yml",
        "data/website_settings.yml",
        "data/apps.xml",

        # Security
        "security/ir_rule.xml",
        "security/res_groups.xml",
        "security/res_users.xml",
        "security/ir.model.access.csv",

        # Data
        'data/res_currency.xml',
        'data/company.xml',
        'data/website.xml',
        'data/project_tags.xml',
        "data/ir_actions_server.xml",
        "data/base_automation.xml",
        "data/hr_timesheet_invoice_data.xml",
        "data/product.xml",
        "data/project.xml",
        "data/project_task_estimation.xml",
        "data/jobs.xml",
        "data/blog.xml",

        # Views
        # Backend stuff (A file per app)
        "views/helpdesk.xml",
        "views/project.xml",
        "views/account_analytic_line_view.xml",
        # "views/hr_timesheet_reports_view.xml",
        "views/hr_timesheet_view.xml",
        "views/menu.xml",
        'views/sale_view.xml',

        # Reports
        "report/layout.xml",
        "report/timesheet_template.xml",
        'report/sale_report_templates.xml',

        # Wizards (One Per Wizard)
        "wizard/set_invoice_view.xml",
        "views/wizard_view.xml",

        # Email templates
        "views/ask_review_criteria_email.xml",
        "views/approve_criteria_email.xml",
        # "views/hr_timesheet_reports_email.xml",
        "data/website_quotation_template.xml",
        "views/approving_start_to_work_email.xml",

        # Stages Data
        "data/project_task_stages.xml",
    ],
    "demo": [
        "demo/product.xml",
        "demo/project.xml",
        "demo/helpdesk.xml",
        "demo/blog.xml",
    ],
    "test": [
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
