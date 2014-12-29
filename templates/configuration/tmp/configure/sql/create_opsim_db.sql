create database OpsimDB;
create user '{{OPSIM_USER}}'@'localhost' identified by '{{OPSIM_PASS}}';
grant all on OpsimDB.* to '{{OPSIM_USER}}'@'localhost';
drop schema OpsimDB;
source {{OPSIM_DIR}}/DataForInstall/sql/v3_0.sql;
grant all privileges on OpsimDB.* to '{{OPSIM_USER}}'@'localhost' identified by '{{OPSIM_PASS}}' with grant option;
flush privileges;
