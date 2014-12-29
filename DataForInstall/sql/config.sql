# 
# Configuration tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS Config;

# AstroConf
CREATE TABLE Config (
    configID    int unsigned AUTO_INCREMENT PRIMARY KEY,
    sessionID   int unsigned NOT NULL COMMENT 'session id',
    propID      int unsigned NULL COMMENT 'proposal ID if relevant',
    moduleName  varchar (20) NOT NULL COMMENT 'module name',
    paramIndex  int NOT NULL COMMENT 'index of parameter for module',
    paramName   varchar (25) NOT NULL COMMENT 'parameter name',
    paramValue  varchar (60) NOT NULL COMMENT 'string of parameter value',
    comment	varchar (20) NULL COMMENT 'comment'
);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on Config to www;

