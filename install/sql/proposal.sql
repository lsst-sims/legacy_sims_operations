# 
# Proposal related tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS Proposal;

# Proposal
CREATE TABLE Proposal (
    propID    int unsigned AUTO_INCREMENT PRIMARY KEY,
    propConf  varchar(255) NOT NULL COMMENT 'proposal configuration filename name',
    propName  varchar(80) NOT NULL COMMENT 'proposal name',
    sessionID int unsigned NOT NULL COMMENT 'session identifier',
    objectID  bigint NULL COMMENT 'python obj identifier for Proposal instance',
    objectHost  varchar(80) NULL COMMENT 'hostname for proposal object instance'
);
CREATE INDEX p_sessID_idx ON Proposal (sessionID);
CREATE INDEX p_sessID_propID_idx ON Proposal (sessionID,propID);


# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on Proposal to www;

