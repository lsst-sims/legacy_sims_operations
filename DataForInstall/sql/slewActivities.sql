# 
# Slew Activities tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS SlewActivities;

# SlewActivities
CREATE TABLE SlewActivities (
  slewActivityID	bigint AUTO_INCREMENT PRIMARY KEY,
  sessionID		int unsigned NOT NULL COMMENT 'session identifier',
  slewCount		bigint NOT NULL COMMENT 'slew count in the run',
  activity		varchar(16) NOT NULL COMMENT 'slew activity name',
  delay			float NOT NULL COMMENT 'slew activity delay in sec',
  inCriticalPath	varchar(6) NOT NULL COMMENT 'bool, is this activity in the critical path of the total slew delay?'
  )
  MAX_ROWS=4000000000;

CREATE INDEX sa_sessID_slewCount_idx ON SlewActivities (sessionID, slewCount);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on SlewActivities to www;

