# 
# Slew History tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS SlewHistory;


# SlewHistory
CREATE TABLE SlewHistory (
  slewID	bigint AUTO_INCREMENT PRIMARY KEY,
  sessionID	int unsigned NOT NULL COMMENT 'session identifier',
  slewCount	bigint NOT NULL COMMENT 'slew count in the run',
  startDate	float NOT NULL COMMENT 'simulation sec, slew start date',
  endDate	float NOT NULL COMMENT 'simulation sec, slew end date (shutter open)',
  delay		float NOT NULL COMMENT 'slew total delay in sec'
);
CREATE INDEX sh_sessID_slewCount_idx ON SlewHistory (sessionID, slewCount);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on SlewHistory to www;

