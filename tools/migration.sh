PGHOST=$1
PGPASSWORD=$2
PGUSER=$3
PGPORT=$4

DATABASE=$5
ADMINLOGIN=$6
ADMINPASSWORD=$7
MIGRATIONLOGIN=$8
MIGRATIONPWD=$9
MIGRATIONBRANCH=${10}
ODOOHOST=${11}
ODOOPORT=${12}

LEGACYDB=${13}
LEGACYPORT=${14}
LEGACYPWD=${15}
LEGACYUSER=${16}

echo $'\nStep 1: Stop odoo server'
supervisorctl stop odoo

echo $'\nStep 2: Export variables to connect to the database'
export PGHOST=$PGHOST
export PGPASSWORD=$PGPASSWORD
export PGUSER=$PGUSER

echo $'\nStep 3: Delete database if exists'
dropdb $DATABASE --if-exist

echo $'\nStep 4: Checkout into clean odoo/saas-14 and instance/vauxoo branch'
cd /home/odoo/instance/odoo
git reset --hard
git clean -dxf
git checkout saas-14
cd /home/odoo/instance/extra_addons/instance
git clean -dxf
git reset --hard
git checkout 10.0

echo $'\nStep 5: Restart odoo server'
supervisorctl start odoo

echo $'\nStep 6: Create new database '$DATABASE' with vauxoo module installed'
export COUNTRY="MX"
python /home/odoo/instance/odoo/odoo-bin -c /home/odoo/.openerp_serverrc -d $DATABASE -i vauxoo --without-demo=all --stop-after-init

echo $'\nStep 7: Update current administrator user name and password'
psql $DATABASE -c "UPDATE res_users SET login='"$ADMINLOGIN"', password = '"$ADMINPASSWORD"' WHERE id=1;"

echo $'\nStep 8: Deactivate the automated actions so do not get messy in the migration process'
psql $DATABASE -c "UPDATE base_automation SET active='f' WHERE id=1;"

echo $'\nStep 9: Checkout migration script branch ' $MIGRATIONBRANCH
cd /home/odoo/instance/extra_addons/instance
su -c "git fetch vauxoo-dev $MIGRATIONBRANCH" odoo
su -c "git checkout $MIGRATIONBRANCH" odoo
su -c "git pull vauxoo-dev $MIGRATIONBRANCH" odoo

echo $'\nStep 10: Create migration user (duplicate from admin)'
python /home/odoo/instance/extra_addons/instance/tools/create_migration_user.py --host $ODOOHOST --port $ODOOPORT --database $DATABASE --user $ADMINLOGIN --password $ADMINPASSWORD --login $MIGRATIONLOGIN --newpwd $MIGRATIONPWD

echo $'\nStep 11: Checkout patch to let us set magic fields (create/update dates and users)'
cd /home/odoo/instance/odoo
su -c "git remote add vauxoo-dev git@github.com:vauxoo-dev/odoo.git" odoo 
su -c "git fetch vauxoo-dev saas-14-vauxoo-patch-kty" odoo
su -c "git reset --hard" odoo
su -c "git clean -xdf" odoo
su -c "git checkout saas-14-vauxoo-patch-kty" odoo
su -c "git pull vauxoo-dev saas-14-vauxoo-patch-kty" odoo

echo $'\nStep 12: Restart Odoo sever to use the new patch/migration specs'
supervisorctl stop odoo
supervisorctl start odoo

# TODO uncomment this if error in tasks and need to re load the timesheets
# psql $DATABASE -c 'delete from account_analytic_line;'
# psql $DATABASE -c "delete from ir_model_data where model = 'account.analytic.line';"
# psql $DATABASE -c "VACUUM FULL;"

echo $'\nStep 13: Configure migration script'
cd /home/odoo/instance/extra_addons/instance/tools
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

echo $'\nStep 14: Run the migration script'
time vxmigration --use-config

echo ' ---------------------- SQL Scripts ------------------------------------'

echo $'\nStep 15: Prepare database to run sql scripts'
su - postgres -c "psql -d $DATABASE -c 'create extension dblink;'"

echo $'\nStep 16: Set scripts parameters (confidential credentials)'
sed -i 's/host= dbname= user= password=/host='$PGHOST' dbname='$LEGACYDB' user='$PGUSER' password='$PGPASSWORD'/g' import_msq_from_v8_to_saas.sql import_attch_from_v8_to_saas.sql

echo $'\nStep 17: Clean up the messages, attachment and followers doing the migration'
su - postgres -c "psql -f cleaunp_msg_attch_followers.sql -d $DATABASE"

echo $'\nStep 18: Migrate the mail messages'
time psql -f import_msq_from_v8_to_saas.sql -d $DATABASE

echo $'\nStep 19: Migrate the attachments'
time psql -f import_attch_from_v8_to_saas.sql -d $DATABASE

echo ' ---------------------- Clean Up -------------------------------------'

echo $'\nStep 20: Return Odoo to normal (without special user patch)'
cd /home/odoo/instance/odoo
git checkout saas-14

echo $'\nStep 21: Return Instance modules to normal 10.0 (display_name store = True'
cd /home/odoo/instance/extra_addons/instance
git checkout -- tools
git checkout 10.0

echo $'\nStep 22: Re activate the automated actions'
psql $DATABASE -c 'UPDATE base_automation SET active='t' WHERE id=1;'

echo $'\nStep 23: Stop Odoo server to get the new changes'
supervisorctl stop odoo

echo $'\nStep 24: Update database'
python /home/odoo/instance/odoo/odoo-bin -c /home/odoo/.openerp_serverrc -d $DATABASE -i hr_timesheet_sheet --stop-after-init
python /home/odoo/instance/odoo/odoo-bin -c /home/odoo/.openerp_serverrc -d $DATABASE -u all --stop-after-init

echo $'\nStep 25: Start Odoo server normally'
supervisorctl start odoo
