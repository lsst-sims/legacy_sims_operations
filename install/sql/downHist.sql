# 
# Non Observing Block related tables
#
#  Login as 'root' when invoking.
                                                                                
USE LSST;
                                                                                
# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS DownHist;
                                                                                
# DownHist
CREATE TABLE DownHist (
    downHistID   int unsigned AUTO_INCREMENT PRIMARY KEY,
    sessionID   int unsigned NOT NULL COMMENT 'session identifier',
    activity    varchar(80) NOT NULL COMMENT 'reason for not observing',
    duration    int unsigned NOT NULL COMMENT 'lost observing time -only nights (secs)',
    startTime   int unsigned NOT NULL COMMENT 'start not observing (simtime)',
    endTime     int unsigned NOT NULL COMMENT 'end not observing (simtime)',
    startNight  int unsigned NOT NULL COMMENT 'start (night count)',
    endNight	int unsigned NOT NULL COMMENT 'end (night count)',
    cloudiness  float NOT NULL COMMENT 'range[0:1] Cloud transparency at start of block, 0=photometric, 0<x<.7=spectroscopic, .7<x<1=opaque',
    scheduled   varchar(6) NOT NULL COMMENT 'bool, scheduled or not (random)'
);
                                                                                
CREATE INDEX DH_sessID_dhID_idx ON DownHist (sessionID, downHistID);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on DownHist to www;
