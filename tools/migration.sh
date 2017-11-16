#!/bin/bash
source migration.conf

START_DATETIME="$(date +%Y-%m-%d_%H-%M)"
ODOO_LOG_FILE="${LOG_DIR}/${START_DATETIME}_server.log"
LOG_FILE="${LOG_DIR}/${START_DATETIME}_migration.log"

ODOO_STOP="supervisorctl stop odoo"
ODOO_START="supervisorctl start odoo"
TOOLS_DIR="${INSTANCE_DIR}/tools"

exec > >(tee -a ${LOG_FILE} )
exec 2> >(tee -a ${LOG_FILE} >&2)

echo 'You can check the logs in'
echo $LOG_FILE
echo $ODOO_LOG_FILE

echo $'\nStep 1: Stop odoo server'
eval $ODOO_STOP

set -e

echo $'\nStep 2: Reset Odoo in order to continue'
cd $ODOO_PATH
git reset --hard

echo $'\nStep 3: Delete database if exists ' $DATABASE ' and delete also the related filestore'
dropdb -h $PGHOST -p $PGPORT -U $PGUSER -w $DATABASE --if-exist
rm $DB_FILESTORE/$DATABASE -rf

echo $'\nStep 4: Create new database '$DATABASE' with vauxoo module installed'
su -c "COUNTRY='MX' python3.5 $ODOO_PATH/odoo-bin -c /home/odoo/.openerp_serverrc -d $DATABASE -i vauxoo --without-demo=all --stop-after-init -r $PGUSER -w $PGPASSWORD --db_host=$PGHOST --db_port=$PGPORT"

echo $'\nStep 5: Restart odoo server'
eval $ODOO_START

echo $'\nStep 6: Update current administrator user name and password'
psql -h $PGHOST -p $PGPORT -U $PGUSER -w -d $DATABASE -c "UPDATE res_users SET login='"$ADMINLOGIN"', password = '"$ADMINPASSWORD"' WHERE id=1;"

echo $'\nStep 7: Deactivate the automated actions so do not get messy in the migration process'
psql -h $PGHOST -p $PGPORT -U $PGUSER -w -d $DATABASE -c "UPDATE base_automation SET active='f' WHERE id=1;"

echo $'\nStep 8: Configure migration script'
cd ${TOOLS_DIR}
pip install --editable .
vxmigration --save-config
echo '
{"legacy_db": "'$LEGACYDB'",
 "legacy_host": "'$LEGACYHOST'",
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
 "nuser": "'$MIGRATIONLOGIN'"}' > $CONFIG_PATH

echo $'\nStep 9: Create migration user (duplicate from admin)'
python3.5 ${TOOLS_DIR}/create_migration_user.py --host $ODOOHOST --port $ODOOPORT --database $DATABASE --user $ADMINLOGIN --password $ADMINPASSWORD --login $MIGRATIONLOGIN --newpwd $MIGRATIONPWD

echo $'\nStep 10: Checkout patch to let us set magic fields (create/update dates and users)'
cd $ODOO_PATH
git reset --hard
git apply -v ${TOOLS_DIR}/odoo-saas14-magic-fields.patch

echo $'\nStep 11: Restart Odoo sever to use the new patch/migration specs'
eval $ODOO_STOP
eval $ODOO_START

echo $'\nStep 12: Wait until database has been innitiate (one minute)'
sleep 60

echo $'\nStep 13: Run the migration script'
time vxmigration --use-config

echo ' ---------------------- SQL Scripts ------------------------------------'

psql -d postgres -c "SHOW SERVER_VERSION;"

echo $'\nStep 14: Prepare database to run sql scripts'
psql -d $DATABASE -c 'CREATE EXTENSION IF NOT EXISTS dblink;'

echo $'\nStep 15: Set scripts parameters (confidential credentials)'
sed -i 's/host= port= dbname= user= password=/host='$LEGACYPGHOST' port='$LEGACYPGPORT' dbname='$LEGACYDB' user='$LEGACYPGUSER' password='$LEGACYPGPASSWORD'/g' import_msq_from_v8_to_saas.sql import_attch_from_v8_to_saas.sql

echo $'\nStep 16: Clean up the messages, attachment and followers doing the migration'
psql -f $TOOLS_DIR/cleaunp_msg_attch_followers.sql -d $DATABASE

echo $'\nStep 17: Migrate the mail messages'
time psql -f $TOOLS_DIR/import_msq_from_v8_to_saas.sql -d $DATABASE

echo $'\nStep 18: Migrate the attachments'
time psql -f $TOOLS_DIR/import_attch_from_v8_to_saas.sql -d $DATABASE

echo ' ---------------------- Clean Up -------------------------------------'

echo $'\nStep 19: Return Odoo to normal (without special user patch)'
cd $ODOO_PATH
git reset --hard

echo $'\nStep 20: Re activate the automated actions'
psql $DATABASE -c "UPDATE base_automation SET active='t' WHERE id=1;"

echo $'\nStep 21: Stop Odoo server to get the new changes'
eval $ODOO_STOP

echo $'\nStep 22: Copy the filestore of legacy to new instance'
cd $DB_FILESTORE
rsync -Pavhe cp --ignore-existing $LEGACYDB/ $DATABASE/

echo $'\nStep 23: Update database with -u all'
python3.5 $ODOO_PATH/odoo-bin -c /home/odoo/.openerp_serverrc -d $DATABASE -u all --stop-after-init

echo $'\nStep 24: Start Odoo server normally'
eval $ODOO_START

END_DATETIME="$(date +%Y-%m-%d_%H-%M)"
echo 'Script start at ' $START_DATETIME ' and ends at ' $END_DATETIME
echo 'You can check the logs in'
echo $ODOO_LOG_FILE
echo $LOG_FILE
