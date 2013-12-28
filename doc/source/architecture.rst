.. _architecture.rst:

*********************
Database Architecture
*********************

The OpSim runs with the help of the following tables ::

	+--------------------------+
	| Tables names             |
	+==========================+
	| Cloud                    |
	| Config                   |
	| Config_File              |
	| Field                    |
	| Log                      |
	| MissedHistory            |
	| ObsHistory               |
	| ObsHistory_Proposal      |
	| Proposal                 |
	| Proposal_Field           |
	| Seeing                   |
	| SeqHistory               |
	| SeqHistory_MissedHistory |
	| SeqHistory_ObsHistory    |
	| Session                  |
	| SlewActivities           |
	| SlewHistory              |
	| SlewMaxSpeeds            |
	| SlewState                |
	| TimeHistory              |
	+--------------------------+

See :download:`Database Schema for v3.0 <_static/v3_0.png>` for a more detailed explanation of table relationships. ::

	+---------+------------+------+-----+---------+----------------+
	| Field   | Type       | Null | Key | Default | Extra          |
	+---------+------------+------+-----+---------+----------------+
	| cloudID | int(11)    | NO   | PRI | NULL    | auto_increment |
	| c_date  | bigint(20) | NO   |     | NULL    |                |
	| cloud   | double     | NO   |     | NULL    |                |
	+---------+------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| configID          | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
	| moduleName        | varchar(64)      | NO   |     | NULL    |                |
	| paramIndex        | int(11)          | NO   |     | NULL    |                |
	| paramName         | varchar(64)      | NO   |     | NULL    |                |
	| paramValue        | varchar(64)      | NO   |     | NULL    |                |
	| comment           | varchar(512)     | YES  |     | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	| nonPropID         | int(10)          | YES  |     | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| config_fileID     | int(11)          | NO   | PRI | NULL    | auto_increment |
	| filename          | varchar(45)      | NO   |     | NULL    |                |
	| data              | blob             | NO   |     | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

	+----------+------------------+------+-----+---------+----------------+
	| Field    | Type             | Null | Key | Default | Extra          |
	+----------+------------------+------+-----+---------+----------------+
	| fieldID  | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
	| fieldFov | double           | NO   | MUL | NULL    |                |
	| fieldRA  | double           | NO   |     | NULL    |                |
	| fieldDec | double           | NO   |     | NULL    |                |
	| fieldGL  | double           | NO   |     | NULL    |                |
	| fieldGB  | double           | NO   |     | NULL    |                |
	| fieldEL  | double           | NO   |     | NULL    |                |
	| fieldEB  | double           | NO   |     | NULL    |                |
	+----------+------------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| logID             | int(10)          | NO   | PRI | NULL    | auto_increment |
	| log_name          | varchar(64)      | NO   |     | NULL    |                |
	| log_value         | varchar(512)     | NO   |     | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| missedHistID      | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
	| Session_sessionID | int(10) unsigned | NO   | PRI | NULL    |                |
	| filter            | varchar(8)       | NO   | MUL | NULL    |                |
	| expDate           | int(10) unsigned | NO   |     | NULL    |                |
	| expMJD            | double           | NO   |     | NULL    |                |
	| night             | int(10) unsigned | NO   |     | NULL    |                |
	| lst               | double           | NO   |     | NULL    |                |
	| Field_fieldID     | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+-------+
	| Field             | Type             | Null | Key | Default | Extra |
	+-------------------+------------------+------+-----+---------+-------+
	| obsHistID         | int(10) unsigned | NO   | PRI | NULL    |       |
	| Session_sessionID | int(10) unsigned | NO   | PRI | NULL    |       |
	| filter            | varchar(8)       | NO   | MUL | NULL    |       |
	| expDate           | int(10) unsigned | NO   |     | NULL    |       |
	| expMJD            | double           | NO   |     | NULL    |       |
	| night             | int(10) unsigned | NO   |     | NULL    |       |
	| visitTime         | double           | NO   |     | NULL    |       |
	| visitExpTime      | double           | NO   |     | NULL    |       |
	| finRank           | double           | NO   |     | NULL    |       |
	| finSeeing         | double           | NO   |     | NULL    |       |
	| transparency      | double           | NO   |     | NULL    |       |
	| airmass           | double           | NO   |     | NULL    |       |
	| vSkyBright        | double           | NO   |     | NULL    |       |
	| filtSkyBright     | double           | NO   |     | NULL    |       |
	| rotSkyPos         | double           | NO   |     | NULL    |       |
	| lst               | double           | NO   |     | NULL    |       |
	| alt               | double           | NO   |     | NULL    |       |
	| az                | double           | NO   |     | NULL    |       |
	| dist2Moon         | double           | NO   |     | NULL    |       |
	| solarElong        | double           | NO   |     | NULL    |       |
	| moonRA            | double           | NO   |     | NULL    |       |
	| moonDec           | double           | NO   |     | NULL    |       |
	| moonAlt           | double           | NO   |     | NULL    |       |
	| moonAZ            | double           | NO   |     | NULL    |       |
	| moonPhase         | double           | NO   |     | NULL    |       |
	| sunAlt            | double           | NO   |     | NULL    |       |
	| sunAZ             | double           | NO   |     | NULL    |       |
	| phaseAngle        | double           | NO   |     | NULL    |       |
	| rScatter          | double           | NO   |     | NULL    |       |
	| mieScatter        | double           | NO   |     | NULL    |       |
	| moonIllum         | double           | NO   |     | NULL    |       |
	| moonBright        | double           | NO   |     | NULL    |       |
	| darkBright        | double           | NO   |     | NULL    |       |
	| rawSeeing         | double           | NO   |     | NULL    |       |
	| wind              | double           | NO   |     | NULL    |       |
	| humidity          | double           | NO   |     | NULL    |       |
	| Field_fieldID     | int(10) unsigned | NO   | MUL | NULL    |       |
	+-------------------+------------------+------+-----+---------+-------+

	+------------------------------+------------------+------+-----+---------+----------------+
	| Field                        | Type             | Null | Key | Default | Extra          |
	+------------------------------+------------------+------+-----+---------+----------------+
	| obsHistory_propID            | int(10)          | NO   | PRI | NULL    | auto_increment |
	| Proposal_propID              | int(10) unsigned | NO   |     | NULL    |                |
	| propRank                     | double           | NO   |     | NULL    |                |
	| ObsHistory_obsHistID         | int(10) unsigned | NO   | MUL | NULL    |                |
	| ObsHistory_Session_sessionID | int(10) unsigned | NO   |     | NULL    |                |
	+------------------------------+------------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| propID            | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
	| propConf          | varchar(255)     | NO   |     | NULL    |                |
	| propName          | varchar(80)      | NO   |     | NULL    |                |
	| objectID          | bigint(20)       | NO   |     | NULL    |                |
	| objectHost        | varchar(80)      | NO   |     | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| proposal_field_id | int(10)          | NO   | PRI | NULL    | auto_increment |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	| Proposal_propID   | int(10) unsigned | NO   | MUL | NULL    |                |
	| Field_fieldID     | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

	+----------+------------+------+-----+---------+----------------+
	| Field    | Type       | Null | Key | Default | Extra          |
	+----------+------------+------+-----+---------+----------------+
	| seeingID | int(11)    | NO   | PRI | NULL    | auto_increment |
	| s_date   | bigint(20) | NO   |     | NULL    |                |
	| seeing   | double     | NO   |     | NULL    |                |
	+----------+------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| sequenceID        | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
	| startDate         | int(10) unsigned | NO   |     | NULL    |                |
	| expDate           | int(10) unsigned | NO   |     | NULL    |                |
	| seqnNum           | int(10) unsigned | NO   |     | NULL    |                |
	| completion        | double           | NO   |     | NULL    |                |
	| reqEvents         | int(10) unsigned | NO   |     | NULL    |                |
	| actualEvents      | int(10) unsigned | NO   |     | NULL    |                |
	| endStatus         | int(10) unsigned | NO   |     | NULL    |                |
	| parent_sequenceID | int(10)          | NO   |     | NULL    |                |
	| Field_fieldID     | int(10) unsigned | NO   | MUL | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	| Proposal_propID   | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

	+---------------------------------+------------------+------+-----+---------+----------------+
	| Field                           | Type             | Null | Key | Default | Extra          |
	+---------------------------------+------------------+------+-----+---------+----------------+
	| seqhistory_missedHistID         | int(10)          | NO   | PRI | NULL    | auto_increment |
	| SeqHistory_sequenceID           | int(10) unsigned | NO   | MUL | NULL    |                |
	| MissedHistory_missedHistID      | int(10) unsigned | NO   | MUL | NULL    |                |
	| MissedHistory_Session_sessionID | int(10) unsigned | NO   |     | NULL    |                |
	+---------------------------------+------------------+------+-----+---------+----------------+

	+------------------------------+------------------+------+-----+---------+----------------+
	| Field                        | Type             | Null | Key | Default | Extra          |
	+------------------------------+------------------+------+-----+---------+----------------+
	| seqhistory_obsHistID         | int(10)          | NO   | PRI | NULL    | auto_increment |
	| SeqHistory_sequenceID        | int(10) unsigned | NO   | MUL | NULL    |                |
	| ObsHistory_obsHistID         | int(10) unsigned | NO   | MUL | NULL    |                |
	| ObsHistory_Session_sessionID | int(10) unsigned | NO   |     | NULL    |                |
	+------------------------------+------------------+------+-----+---------+----------------+

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| timeHistID        | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
	| date              | int(10) unsigned | NO   |     | NULL    |                |
	| mjd               | double           | NO   |     | NULL    |                |
	| night             | int(10) unsigned | NO   |     | NULL    |                |
	| event             | int(10) unsigned | NO   | MUL | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

	+-------------+------------------+------+-----+---------+----------------+
	| Field       | Type             | Null | Key | Default | Extra          |
	+-------------+------------------+------+-----+---------+----------------+
	| sessionID   | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
	| sessionUser | varchar(80)      | NO   | MUL | NULL    |                |
	| sessionHost | varchar(80)      | NO   |     | NULL    |                |
	| sessionDate | datetime         | NO   |     | NULL    |                |
	| version     | varchar(20)      | YES  |     | NULL    |                |
	| runComment  | varchar(200)     | YES  |     | NULL    |                |
	+-------------+------------------+------+-----+---------+----------------+

	+--------------------+-------------+------+-----+---------+----------------+
	| Field              | Type        | Null | Key | Default | Extra          |
	+--------------------+-------------+------+-----+---------+----------------+
	| slewActivityID     | bigint(20)  | NO   | PRI | NULL    | auto_increment |
	| activity           | varchar(16) | NO   |     | NULL    |                |
	| actDelay           | double      | NO   |     | NULL    |                |
	| inCriticalPath     | varchar(16) | NO   |     | NULL    |                |
	| SlewHistory_slewID | bigint(20)  | NO   | MUL | NULL    |                |
	+--------------------+-------------+------+-----+---------+----------------+

	+------------------------------+------------------+------+-----+---------+----------------+
	| Field                        | Type             | Null | Key | Default | Extra          |
	+------------------------------+------------------+------+-----+---------+----------------+
	| slewID                       | bigint(20)       | NO   | PRI | NULL    | auto_increment |
	| slewCount                    | bigint(20)       | NO   |     | NULL    |                |
	| startDate                    | double           | NO   |     | NULL    |                |
	| endDate                      | double           | NO   |     | NULL    |                |
	| slewTime                     | double           | NO   |     | NULL    |                |
	| slewDist                     | double           | NO   |     | NULL    |                |
	| ObsHistory_obsHistID         | int(10) unsigned | NO   | MUL | NULL    |                |
	| ObsHistory_Session_sessionID | int(10) unsigned | NO   |     | NULL    |                |
	+------------------------------+------------------+------+-----+---------+----------------+

	+--------------------+------------+------+-----+---------+----------------+
	| Field              | Type       | Null | Key | Default | Extra          |
	+--------------------+------------+------+-----+---------+----------------+
	| slewMaxSpeedID     | bigint(20) | NO   | PRI | NULL    | auto_increment |
	| domAltSpd          | double     | NO   |     | NULL    |                |
	| domAzSpd           | double     | NO   |     | NULL    |                |
	| telAltSpd          | double     | NO   |     | NULL    |                |
	| telAzSpd           | double     | NO   |     | NULL    |                |
	| rotSpd             | double     | NO   |     | NULL    |                |
	| SlewHistory_slewID | bigint(20) | NO   | MUL | NULL    |                |
	+--------------------+------------+------+-----+---------+----------------+

	+--------------------+-------------+------+-----+---------+----------------+
	| Field              | Type        | Null | Key | Default | Extra          |
	+--------------------+-------------+------+-----+---------+----------------+
	| slewIniStatID      | bigint(20)  | NO   | PRI | NULL    | auto_increment |
	| slewStateDate      | double      | NO   |     | NULL    |                |
	| tra                | double      | NO   |     | NULL    |                |
	| tdec               | double      | NO   |     | NULL    |                |
	| tracking           | varchar(16) | NO   |     | NULL    |                |
	| alt                | double      | NO   |     | NULL    |                |
	| az                 | double      | NO   |     | NULL    |                |
	| pa                 | double      | NO   |     | NULL    |                |
	| domAlt             | double      | NO   |     | NULL    |                |
	| domAz              | double      | NO   |     | NULL    |                |
	| telAlt             | double      | NO   |     | NULL    |                |
	| telAz              | double      | NO   |     | NULL    |                |
	| rotTelPos          | double      | NO   |     | NULL    |                |
	| filter             | varchar(8)  | NO   |     | NULL    |                |
	| state              | int(10)     | NO   |     | NULL    |                |
	| SlewHistory_slewID | bigint(20)  | NO   | MUL | NULL    |                |
	+--------------------+-------------+------+-----+---------+----------------+









