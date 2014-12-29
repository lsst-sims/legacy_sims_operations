# 
# Missed Observations History  related tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS MissedHistory;


# MissedHistory
CREATE TABLE MissedHistory (
    missedHistID  int unsigned AUTO_INCREMENT PRIMARY KEY,
    sessionID  int unsigned NOT NULL COMMENT 'session identifier',
    propID     int unsigned NOT NULL COMMENT 'proposal identifier',
    fieldID    int unsigned NOT NULL COMMENT 'field identifier',
    filter     varchar(8)   NOT NULL COMMENT 'filter name',
    seqnNum    int unsigned          COMMENT 'sequence number in the proposal',
    subseq     varchar(8)   NOT NULL COMMENT 'subsequence name',
    pairNum    int unsigned NOT NULL COMMENT 'pair number in the subsequence',
    misDate    int unsigned NOT NULL COMMENT 'sec, date relative to 0s at start',
    misMJD     double NOT NULL COMMENT 'modified julian date, exposure date',
    fieldRA    float NOT NULL COMMENT 'radians, field right ascension',
    fieldDec   float NOT NULL COMMENT 'radians, field declination'
);
CREATE INDEX mh_sessID_idx ON MissedHistory (sessionID);
CREATE INDEX mh_propID_idx ON MissedHistory (sessionID,propID);
CREATE INDEX mh_field_filter_idx ON MissedHistory (sessionID, fieldID, filter);
CREATE INDEX mh_seqnNum_subseq_idx ON MissedHistory (sessionID, seqnNum, subseq);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on MissedHistory to www;

