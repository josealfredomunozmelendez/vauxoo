#!/bin/bash
source migration.conf

START_DATETIME="$(date +%Y-%m-%d_%H-%M)"
LOG_FILE="$HOME/${START_DATETIME}_migration.log"

exec > >(tee -a ${LOG_FILE} )
exec 2> >(tee -a ${LOG_FILE} >&2)

echo 'You can check the logs in'
echo $LOG_FILE

set -e

echo $'\nStep 1: Update current administrator user name and password'
PGPASSWORD=$PGPASSWORD psql -h $PGHOST -p $PGPORT -U $PGUSER -w -d $DATABASE -c "UPDATE res_users SET login='"$ADMINLOGIN"', password = '"$ADMINPASSWORD"' WHERE id=1;"

echo $'\nStep 2: Deactivate the automated actions so do not get messy in the migration process'
PGPASSWORD=$PGPASSWORD psql -h $PGHOST -p $PGPORT -U $PGUSER -w -d $DATABASE -c "UPDATE base_automation SET active='f' WHERE id=1;"

echo $'\nStep 3: Configure migration script'
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
 "nuser": "'$MIGRATIONLOGIN'"}' > $HOME/.vxmigration

echo $'\nStep 4: Create migration user (duplicate from admin)'
python3.5 ./create_migration_user.py --host $ODOOHOST --port $ODOOPORT --database $DATABASE --user $ADMINLOGIN --password $ADMINPASSWORD --login $MIGRATIONLOGIN --newpwd $MIGRATIONPWD

echo $'\nStep 5: Run the migration script'
time vxmigration --use-config

echo ' ---------------------- SQL Scripts ------------------------------------'

PGPASSWORD=$PGPASSWORD psql -h $PGHOST -p $PGPORT -U $PGUSER -w -d postgres -c "SHOW SERVER_VERSION;"

echo $'\nStep 6: Prepare database to run sql scripts'
PGPASSWORD=$PGPASSWORD psql  -h $PGHOST -p $PGPORT -U $PGUSER -w -d $DATABASE -c 'CREATE EXTENSION IF NOT EXISTS dblink;'

echo $'\nStep 7: Set scripts parameters (confidential credentials)'
sed -i 's/host= port= dbname= user= password=/host='$LEGACYPGHOST' port='$LEGACYPGPORT' dbname='$LEGACYDB' user='$LEGACYPGUSER' password='$LEGACYPGPASSWORD'/g' import_msq_from_v8_to_saas.sql import_attch_from_v8_to_saas.sql

echo $'\nStep 8: Clean up the messages, attachment and followers doing the migration'
PGPASSWORD=$PGPASSWORD psql -h $PGHOST -p $PGPORT -U $PGUSER -w -f cleaunp_msg_attch_followers.sql -d $DATABASE

echo $'\nStep 9: Migrate the mail messages'
time PGPASSWORD=$PGPASSWORD psql -h $PGHOST -p $PGPORT -U $PGUSER -w -f import_msq_from_v8_to_saas.sql -d $DATABASE

echo $'\nStep 10: Migrate the attachments'
time PGPASSWORD=$PGPASSWORD psql -h $PGHOST -p $PGPORT -U $PGUSER -w -f import_attch_from_v8_to_saas.sql -d $DATABASE

echo ' ---------------------- Clean Up -------------------------------------'

echo $'\nStep 11: Re activate the automated actions'
PGPASSWORD=$PGPASSWORD psql -h $PGHOST -p $PGPORT -U $PGUSER -w -d $DATABASE -c "UPDATE base_automation SET active='t' WHERE id=1;"

END_DATETIME="$(date +%Y-%m-%d_%H-%M)"
echo 'Script start at ' $START_DATETIME ' and ends at ' $END_DATETIME
echo 'You can check the logs in'
echo $LOG_FILE
