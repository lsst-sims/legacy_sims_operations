# Password for www user, must match .my.cnf file.
passwd=changeit
# Location of sims_operations directory
code_dir=${SIMS_OPERATIONS_DIR}/DataForInstall

mysql -u root -p -e "create database OpsimDB; create user 'www'@'localhost' identified by '${passwd}'; grant all on OpsimDB.* to 'www'@'localhost';"
mysql -u root -p -e "drop schema OpsimDB; source ${code_dir}/sql/v3_0.sql; grant all privileges on OpsimDB.* to 'www'@'localhost' identified by '${passwd}' with grant option; flush privileges;"

mysql -u www -p${passwd} -e "use OpsimDB;source ${code_dir}/data/current/Cloud.sql;source ${code_dir}/data/current/Seeing.sql;source ${code_dir}/data/current/Field.sql;"
