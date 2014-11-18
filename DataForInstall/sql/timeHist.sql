# 
# Time History  related tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS TimeHistory;


# TimeHistory
CREATE TABLE TimeHistory (
    timeHistID   int unsigned AUTO_INCREMENT PRIMARY KEY,
    sessionID   int unsigned NOT NULL COMMENT 'session identifier',
    date        int unsigned NOT NULL COMMENT 'simulation sec, event date',
    MJD         float NOT NULL COMMENT 'MJD, event date',
    night       int unsigned NOT NULL COMMENT 'count of simulated nights start with 1',
    event       int unsigned NOT NULL COMMENT '0=startNight,1=moon wane,2=moon wax,3=startYear,4=endDusk,5=startDawn,6=endNight'
);
CREATE INDEX th_sessID_idx ON TimeHistory (sessionID);
CREATE INDEX th_sessID_event_idx ON TimeHistory (sessionID,event);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on TimeHistory to www;

