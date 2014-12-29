# 
# Slew Final State tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS SlewFinalState;


# SlewFinalState
CREATE TABLE SlewFinalState (
  slewFinStatID	bigint AUTO_INCREMENT PRIMARY KEY,
  sessionID	int unsigned NOT NULL COMMENT 'session identifier',
  slewCount	bigint NOT NULL COMMENT 'slew count in the run',
  time          float NOT NULL COMMENT 'simulation sec, observation time for RA DEC coordinates',
  tra           float NOT NULL COMMENT 'target RA radians',
  tdec          float NOT NULL COMMENT 'target DEC radians',
  tracking      varchar(6) NOT NULL COMMENT 'bool, tracking state',
  alt           float NOT NULL COMMENT 'target ALT radians',
  az            float NOT NULL COMMENT 'target AZ radians',
  pa            float NOT NULL COMMENT 'target PA radians',
  DomAlt        float NOT NULL COMMENT 'Dome ALT radians',
  DomAz         float NOT NULL COMMENT 'absolute Dome AZ radians',
  TelAlt        float NOT NULL COMMENT 'Telescope ALT radians',
  TelAz         float NOT NULL COMMENT 'absolute Telescope AZ radians',
  RotPos        float NOT NULL COMMENT 'absolute Rotator Angle radians',
  Filter        varchar(8) NOT NULL COMMENT 'Filter position'
);
CREATE INDEX sfs_sessID_slewCount_idx ON SlewFinalState (sessionID, slewCount);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on SlewFinalState to www;

