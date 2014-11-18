# 
# Cerro Pachon  Cloud data table
# 
#  Login as 'root' when invoking. 

USE LSST;

# If the table is already there, drop it
DROP TABLE IF EXISTS CloudTololo;

CREATE TABLE CloudTololo (
  c_date   bigint NOT NULL PRIMARY KEY,     # in seconds since Jan 1 
  cloud  float NOT NULL COMMENT 'range[0:1], Cloud transparency 0= photometric, 0<x<1 = spectroscopic, 1 = opaque'
);
CREATE UNIQUE INDEX c_date_cloud_idx ON CloudTololo (c_date,cloud);


GRANT SELECT, UPDATE, DELETE, INSERT on CloudTololo to www;

