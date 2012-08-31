# 
# Slew Maximum Speeds tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS SlewMaxSpeeds;


# SlewMaxSpeeds
CREATE TABLE SlewMaxSpeeds (
  slewMaxSpeedID	bigint AUTO_INCREMENT PRIMARY KEY,
  sessionID	int unsigned NOT NULL COMMENT 'session identifier',
  slewCount	bigint NOT NULL COMMENT 'slew count in the run',
  DomAltSpd     float NOT NULL COMMENT 'Dome ALT maximum speed radians/sec',
  DomAzSpd      float NOT NULL COMMENT 'absolute Dome AZ maximum speed radians/sec',
  TelAltSpd     float NOT NULL COMMENT 'Telescope ALT maximum speed radians/sec',
  TelAzSpd      float NOT NULL COMMENT 'absolute Telescope AZ maximum speed radians/sec',
  RotSpd	float NOT NULL COMMENT 'absolute Rotator Angle maximum speed radians/sec'
);
CREATE INDEX sms_sessID_slewCount_idx ON SlewMaxSpeeds (sessionID, slewCount);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on SlewMaxSpeeds to www;

