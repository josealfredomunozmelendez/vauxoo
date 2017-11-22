# !/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from vxcommon import connect


def main():
    """ This script will add the create_uid and write_uid for the next list of
    models. This info was not able to be loaded since this ones were loaded
    before migrate the res.users.
    """
    vauxoo = connect()
    vauxoo.install_magic_patch('migration')

    models = [
        'res.company',
        'res.country.state',
        ['regimen.fiscal', 'account.fiscal.position'],
        'res.partner',
        'auth.oauth.provider',
    ]
    export_fields = load_fields = ['id', 'create_uid/id', 'write_uid/id']

    for model in models:
        read_model = model if isinstance(model, str) else model[0]
        write_model = model if isinstance(model, str) else model[1]

        ids = vauxoo.legacy.env[read_model].search([])
        legacy_data = vauxoo.export(read_model, ids, export_fields)
        vauxoo.load(write_model, load_fields, legacy_data)

    vauxoo.uninstall_magic_patch()


if __name__ == '__main__':
    main()
