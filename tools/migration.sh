#!/bin/bash
set -e

PGHOST=$1
PGPASSWORD=$2
PGUSER=$3
PGPORT=$4

DATABASE=$5
ADMINLOGIN=$6
ADMINPASSWORD=$7
MIGRATIONLOGIN=$8
MIGRATIONPWD=$9
ODOOHOST=${10}
ODOOPORT=${11}

LEGACYDB=${12}
LEGACYPORT=${13}
LEGACYPWD=${14}
LEGACYUSER=${15}

INSTANCE_DIR="/home/odoo/instance/extra_addons/instance"
TOOLS_DIR="${INSTANCE_DIR}/tools"
LOG_FILE="/home/odoo/migration_$(date +%Y-%m-%d_%H-%M).log"
exec > >(tee -a ${LOG_FILE} )
exec 2> >(tee -a ${LOG_FILE} >&2)

echo $'\nStep 1: Stop odoo server'
supervisorctl stop odoo

echo $'\nStep 2: Export variables to connect to the database'
export PGHOST=$PGHOST
export PGPASSWORD=$PGPASSWORD
export PGUSER=$PGUSER

echo $'\nStep 3: Delete database if exists ' $DATABASE
dropdb $DATABASE --if-exist

echo $'\nStep 4: Create new database '$DATABASE' with vauxoo module installed'
export COUNTRY="MX"
python /home/odoo/instance/odoo/odoo-bin -c /home/odoo/.openerp_serverrc -d $DATABASE -i vauxoo --without-demo=all --stop-after-init

echo $'\nStep 5: Restart odoo server'
supervisorctl start odoo

echo $'\nStep 6: Update current administrator user name and password'
psql $DATABASE -c "UPDATE res_users SET login='"$ADMINLOGIN"', password = '"$ADMINPASSWORD"' WHERE id=1;"

echo $'\nStep 7: Deactivate the automated actions so do not get messy in the migration process'
psql $DATABASE -c "UPDATE base_automation SET active='f' WHERE id=1;"

echo $'\nStep 8: Checkout patch to let us set magic fields (create/update dates and users)'
cd /home/odoo/instance/odoo
git reset --hard
su -c "git apply -v ${TOOLS_DIR}/odoo-saas14-magic-fields.patch" odoo

echo $'\nStep 9: Wait until database has been innitiate (one minute)'
sleep 60

echo $'\nStep 10: Create migration user (duplicate from admin)'
python ${TOOLS_DIR}/create_migration_user.py --host $ODOOHOST --port $ODOOPORT --database $DATABASE --user $ADMINLOGIN --password $ADMINPASSWORD --login $MIGRATIONLOGIN --newpwd $MIGRATIONPWD

echo $'\nStep 11: Restart Odoo sever to use the new patch/migration specs'
supervisorctl stop odoo
supervisorctl start odoo

echo $'\nStep 12: Configure migration script'
cd ${TOOLS_DIR}
virtualenv venv
. venv/bin/activate
pip install --editable .
echo '
{"legacy_db": "'$LEGACYDB'",
 "legacy_host": "'$ODOOHOST'",
 "legacy_port": '$LEGACYPORT',
 "legacy_pwd": "'$LEGACYPWD'",
 "legacy_user": "'$LEGACYUSER'",
 "dbport": '$PGPORT',
 "dbpwd": "'$PGPASSWORD'",
 "dbhost": "'$PGHOST'",
 "dbuser": "'$PGUSER'",
 "ndb": "'$DATABASE'",
 "nhost": "'$ODOOHOST'",
 "nport": '$ODOOPORT',
 "npwd": "'$MIGRATIONPWD'",
 "nuser": "'$MIGRATIONLOGIN'"}' > /root/.config/vxmigration/config.json

echo $'\nStep 13: Run the migration script'
time vxmigration --use-config

echo ' ---------------------- SQL Scripts ------------------------------------'

echo $'\nStep 14: Prepare database to run sql scripts'
su - postgres -c "psql -d $DATABASE -c 'CREATE EXTENSION IF NOT EXISTS dblink;'"

echo $'\nStep 15: Set scripts parameters (confidential credentials)'
sed -i 's/host= dbname= user= password=/host='$PGHOST' dbname='$LEGACYDB' user='$PGUSER' password='$PGPASSWORD'/g' import_msq_from_v8_to_saas.sql import_attch_from_v8_to_saas.sql

echo $'\nStep 16: Clean up the messages, attachment and followers doing the migration'
su - postgres -c "psql -f $TOOLS_DIR/cleaunp_msg_attch_followers.sql -d $DATABASE"

echo $'\nStep 17: Migrate the mail messages'
time psql -f $TOOLS_DIR/import_msq_from_v8_to_saas.sql -d $DATABASE

echo $'\nStep 18: Migrate the attachments'
time psql -f $TOOLS_DIR/import_attch_from_v8_to_saas.sql -d $DATABASE

echo ' ---------------------- Clean Up -------------------------------------'

echo $'\nStep 19: Return Odoo to normal (without special user patch)'
cd /home/odoo/instance/odoo
git reset --hard

echo $'\nStep 20: Re activate the automated actions'
psql $DATABASE -c "UPDATE base_automation SET active='t' WHERE id=1;"

echo $'\nStep 21: Stop Odoo server to get the new changes'
supervisorctl stop odoo

echo $'\nStep 22: Update database with -u all'
python /home/odoo/instance/odoo/odoo-bin -c /home/odoo/.openerp_serverrc -d $DATABASE -u all --stop-after-init

echo $'\nStep 23: Start Odoo server normally'
supervisorctl start odoo
