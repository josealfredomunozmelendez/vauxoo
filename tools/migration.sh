#!/bin/bash
set -e

source migration.conf

: ${DB_HOST:?}
: ${DB_PORT:?}
: ${DB_NAME:?}
: ${DB_USER:?}
: ${DB_PASSWORD:?}
: ${WORKERS:?}
: ${ODOO_FILESTORE_PATH:?}

START_DATETIME="$(date +%Y-%m-%d_%H-%M)"
LOG_FILE="$HOME/${START_DATETIME}_migration.log"

exec > >(tee -a ${LOG_FILE} )
exec 2> >(tee -a ${LOG_FILE} >&2)

echo 'You can check the logs in'
echo $LOG_FILE

echo $'\nStep 1: Update current administrator user name and password'
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -w -d $DB_NAME -c "UPDATE res_users SET login='"$ADMINLOGIN"', password = '"$ADMINPASSWORD"' WHERE id=1;"

echo $'\nStep 2: Deactivate the automated actions so do not get messy in the migration process'
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -w -d $DB_NAME -c "UPDATE base_automation SET active='f' WHERE id=1;"

echo $'\nStep 3: Create migration user (duplicate from admin)'
python3.5 ./create_migration_user.py --host $ODOOHOST --port $ODOOPORT --database $DB_NAME --user $ADMINLOGIN --password $ADMINPASSWORD --login $MIGRATIONLOGIN --newpwd $MIGRATIONPWD

echo $'\nStep 4: Configure migration script'
pip install --user -r requirements.txt
python3.5 import_data.py --save-config --legacy-db $LEGACYDB --legacy-host $LEGACYHOST --legacy-port $LEGACYPORT --legacy-pwd $LEGACYPWD --legacy-user $LEGACYUSER --dbport $DB_PORT --dbpwd $DB_PASSWORD --dbhost $DB_HOST --dbuser $DB_USER --ndb $DB_NAME --nhost $ODOOHOST --nport $ODOOPORT --npwd $MIGRATIONPWD --nuser $MIGRATIONLOGIN --workers $WORKERS

echo $'\nStep 5: Run the migration script'
python3.5 import_data.py --use-config

echo ' ---------------------- SQL Scripts ------------------------------------'

PCPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -w -d postgres -c "SHOW SERVER_VERSION;"

echo $'\nStep 6: Prepare database to run sql scripts'
PCPASSWORD=$DB_PASSWORD psql  -h $DB_HOST -p $DB_PORT -U $DB_USER -w -d $DB_NAME -c 'CREATE EXTENSION IF NOT EXISTS dblink;'

echo $'\nStep 7: Set scripts parameters (confidential credentials)'
sed -i 's/host= port= dbname= user= password=/host='$LEGACYPGHOST' port='$LEGACYPGPORT' dbname='$LEGACYDB' user='$LEGACYPGUSER' password='$LEGACYPGPASSWORD'/g' import_msq_from_v8_to_saas.sql import_attch_from_v8_to_saas.sql

echo $'\nStep 8: Clean up the messages, attachment and followers doing the migration'
PCPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -w -f cleaunp_msg_attch_followers.sql -d $DB_NAME

echo $'\nStep 9: Migrate the mail messages'
time PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -w -f import_msq_from_v8_to_saas.sql -d $DB_NAME

echo $'\nStep 10: Migrate the attachments'
time PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -w -f import_attch_from_v8_to_saas.sql -d $DB_NAME

echo ' ---------------------- Clean Up -------------------------------------'

echo $'\nStep 11: Re activate the automated actions'
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -w -d $DB_NAME -c "UPDATE base_automation SET active='t' WHERE id=1;"

echo $'\nStep 12: Copy files from vauxoo80 to filestore vauxoo110'
rsync -Pavhe "ssh -p 3202" --ignore-existing fs@files.vauxoo.com:/home/fs/filestore/ $ODOO_FILESTORE_PATH/$DB_NAME/

END_DATETIME="$(date +%Y-%m-%d_%H-%M)"
echo 'Script start at ' $START_DATETIME ' and ends at ' $END_DATETIME
echo 'You can check the logs in'
echo $LOG_FILE
