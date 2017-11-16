# !/usr/bin/env python
# -*- coding: utf-8 -*-
import odoorpc
import click


def conect_and_login(host, port, database, user, password):
    instance = odoorpc.ODOO(host, port=port, timeout=9999999)
    instance.login(database, user, password)
    click.echo(
        "Connected to database %s (%s) in host %s:%s as %s" % (
            database, instance.version, host, port, user))
    return instance


@click.command()
@click.option('--host', default='127.0.0.1',
              help='Odoo  server host. default 127.0.0.1')
@click.option('--port', type=int, default=8069,
              help='Odoo server port. default 8069')
@click.option("--database", type=str, help='Database name')
@click.option("--user", type=str, help='Odoo user')
@click.option("--password", type=str, help='Odoo user password')
@click.option("--login", type=str, help='New user login')
@click.option("--newpwd", type=str, help='New user password')
def main(host=None, port=None, database=None, user=None, password=None,
         login=None, newpwd=None):
    """ This script will connect to a odoo instance and create a new user
    copy of administrator user that will be use for the migration process.
    """
    if None in [host, port, database, user, password, login, newpwd]:
        click.echo("ERROR: Please introduce all the parameters to continue")
        quit()

    saas14 = conect_and_login(host, port, database, user, password)
    migration_user = saas14.execute(
        'res.users', 'search', [('login', '=', login,)])
    if not migration_user:
        migration_user = saas14.execute('res.users', 'copy', [1], {
            'name': login, 'login': login, 'password': newpwd})

    click.echo('New user created with ID %s' % (migration_user,))


if __name__ == '__main__':
    main()
