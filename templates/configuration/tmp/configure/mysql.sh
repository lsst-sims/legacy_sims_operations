#!/usr/bin/env bash

set -e

OPSIM_RUN_DIR={{OPSIM_RUN_DIR}}
PATH={{PATH}}
MYSQL_DIR={{MYSQL_DIR}}
MYSQLD_SOCK={{MYSQLD_SOCK}}
MYSQLD_DATA_DIR={{MYSQLD_DATA_DIR}}
MYSQLD_HOST={{MYSQLD_HOST}}
MYSQLD_PORT={{MYSQLD_PORT}}
MYSQLD_PASS={{MYSQLD_PASS}}
OPSIM_PASS={{OPSIM_PASS}}

SQL_DIR=${OPSIM_RUN_DIR}/tmp/configure/sql

is_socket_available() {
    uname=$(uname)
    # run command in subshell so that we can redirect errors (which are expected)
    if [[ ${uname} == 'Darwin' ]]; then
        (nc -z -w 1 ${MYSQLD_HOST} ${MYSQLD_PORT}) 2>/dev/null
    else
        (timeout 1 bash -c "cat < /dev/null > /dev/tcp/${MYSQLD_HOST}/${MYSQLD_PORT}") 2>/dev/null
    fi
    # status == 1 means that the socket is available
    local status=$?
    local retcode=0
    if [[ ${status} == 0 ]]; then
        echo "WARN: A service is already running on MySQL socket : ${MYSQLD_HOST}:${MYSQLD_PORT}"
	      echo "WARN: Please stop it and relaunch configuration procedure"
        retcode=1
    elif [[ ${status} == 124 ]]; then
	      echo "WARN: A time-out occured while testing MySQL socket state : ${MYSQLD_HOST}:${MYSQLD_PORT}"
	      echo "WARN: Please check that a service doesn't already use this socket, possibly with an other user account"
        retcode=124
    elif [[ ${status} != 1 ]]; then
	      echo "WARN: Unable to test MySQL socket state : ${MYSQLD_HOST}:${MYSQLD_PORT}"
	      echo "WARN: Please check that a service doesn't already use this socket"
        retcode=2
    fi
    return ${retcode}
}

is_socket_available || exit 1

echo "-- Removing previous data." &&
rm -rf ${MYSQLD_DATA_DIR}/* &&
echo "-- ." &&
echo "-- Installing mysql database files." &&
${MYSQL_DIR}/scripts/mysql_install_db --defaults-file=${OPSIM_RUN_DIR}/etc/my.cnf --user=${USER} >/dev/null ||{
    echo "ERROR : mysql_install_db failed, exiting"
    exit 1
}
echo "-- Starting mysql server." &&
${OPSIM_RUN_DIR}/etc/init.d/mysqld start &&
sleep 5 &&
echo "-- Changing mysql root password." &&
mysql --no-defaults -S ${MYSQLD_SOCK} -u root < ${SQL_DIR}/mysql-password.sql &&
rm ${SQL_DIR}/mysql-password.sql &&
echo "-- Setting up OpSim DB." &&
mysql --no-defaults --sock="${MYSQLD_SOCK}" --user="root" --password="${MYSQLD_PASS}" < ${SQL_DIR}/create_opsim_db.sql &&
echo "-- Loading user tables in OpSim DB." &&
mysql --no-defaults --sock="${MYSQLD_SOCK}" --user="www" --password="${OPSIM_PASS}" < ${SQL_DIR}/load_opsim_db.sql &&
echo "-- Shutting down mysql server." &&
${OPSIM_RUN_DIR}/etc/init.d/mysqld stop ||
{
    echo -n "ERROR : Failed to set mysql root user password. "
    echo "Please set the mysql root user password with : "
    echo "mysqladmin -S ${OPSIM_RUN_DIR}/var/lib/mysql/mysql.sock -u root password <password>"
    echo "mysqladmin -u root -h ${MYSQLD_HOST} -P${MYSQLD_PASS} password <password>"
    exit 1
}

echo "INFO: MySQL initialization SUCCESSFUL"
