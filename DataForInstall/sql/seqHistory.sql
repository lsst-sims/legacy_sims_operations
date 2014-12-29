# 
# Sequence History related tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS SeqHistory;


# SeqHistory
CREATE TABLE SeqHistory (
  sequenceID  int unsigned AUTO_INCREMENT PRIMARY KEY,
  sessionID   int unsigned NOT NULL COMMENT 'session identifier',
  startDate   int unsigned NOT NULL COMMENT 'simulation sec, sequence start date',
  expDate     int unsigned NOT NULL COMMENT 'simulation sec, sequence end date',
  propID      int unsigned NOT NULL COMMENT 'proposal identifier',
  fieldID     int unsigned NOT NULL COMMENT 'field identifier',
  seqnNum     int unsigned          COMMENT 'sequence number in the proposal',
  completion  float NOT NULL COMMENT 'completion status, =1 if success, else 0',
  reqEvents   int unsigned NOT NULL COMMENT '# requested events',
  actualEvents int unsigned NOT NULL COMMENT '# events actually acquired',
  endStatus   int unsigned NOT NULL COMMENT 'end status: 0=success,1=max missed events, 2=cycle end'
);
CREATE INDEX sh_sessID_propID_idx ON SeqHistory (sessionID, propID);
CREATE INDEX sh_sessID_field_idx ON SeqHistory (sessionID,fieldID);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on SeqHistory to www;

