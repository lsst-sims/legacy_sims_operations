# 
# Cerro Pachon Seeing data table
# 
#  Login as 'root' when invoking.

USE LSST;

# If the table is already there, drop it
DROP TABLE IF EXISTS SeeingPachon;

CREATE TABLE SeeingPachon (
  s_date   bigint NOT NULL PRIMARY KEY COMMENT 'sec since Jan 1',
  seeing   float NOT NULL COMMENT 'fwhm in arcsec'
);
CREATE UNIQUE INDEX s_date_seeing_idx ON SeeingPachon (s_date,seeing);

GRANT SELECT, UPDATE, DELETE, INSERT on SeeingPachon to www;

