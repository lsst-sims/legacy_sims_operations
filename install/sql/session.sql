# 
# Session related tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS Session;


# Session
CREATE TABLE Session (
    sessionID       int unsigned AUTO_INCREMENT PRIMARY KEY,
    sessionUser     varchar(80) NOT NULL COMMENT 'operator user name',
    sessionHost     varchar(80) NOT NULL COMMENT 'hostname of processor',
    sessionDate     datetime NOT NULL COMMENT 'date of simulation run',
    version	    varchar(20) COMMENT 'software version',
    runComment      varchar(200) COMMENT 'user startup comment'
);
CREATE UNIQUE INDEX s_host_user_date_idx ON Session (sessionUser, sessionHost, sessionDate);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on Session to www;

