
OPSIM_DIR="{{OPSIM_DIR}}"
OPSIM_RUN_DIR="{{OPSIM_RUN_DIR}}"
MYSQL_DIR="{{MYSQL_DIR}}"
MYSQLD_SOCK="{{MYSQLD_SOCK}}"
MYSQLD_USER="{{MYSQLD_USER}}"
MYSQLD_PASS="{{MYSQLD_PASS}}"

SQL_DIR="${OPSIM_RUN_DIR}/tmp/configure/sql"

"${OPSIM_RUN_DIR}"/etc/init.d/mysqld start &&
echo "-- Loading ${SQL_FILE} in MySQL"
"${MYSQL_DIR}"/bin/mysql --no-defaults -vvv --user="${MYSQLD_USER}" \
--password="${MYSQLD_PASS}" --sock="${MYSQLD_SOCK}" < "${SQL_DIR}/${SQL_FILE}" &&
"${OPSIM_RUN_DIR}"/etc/init.d/mysqld stop ||
{
    >&2 echo "ERROR: unable to load ${SQL_FILE}"
    exit 1
}
