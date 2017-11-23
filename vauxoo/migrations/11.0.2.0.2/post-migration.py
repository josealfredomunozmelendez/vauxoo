# coding: utf-8


def disable_email_templates_updates(cr):
    # Disable updates again so the users can modify them without losing data
    cr.execute("UPDATE ir_model_data "
               "SET noupdate = True "
               "WHERE model = 'mail.template'")


def migrate(cr, version):
    if not version:
        return
    disable_email_templates_updates(cr)
