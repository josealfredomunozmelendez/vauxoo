# coding: utf-8


def enable_email_templates_updates(cr):
    # Enable templates updates so they can be updated with the new design
    cr.execute("UPDATE ir_model_data "
               "SET noupdate = False "
               "WHERE model = 'mail.template'")


def migrate(cr, version):
    if not version:
        return
    enable_email_templates_updates(cr)
