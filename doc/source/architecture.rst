.. _architecture.rst:

*********************
Database Architecture
*********************

The OpSim runs in Python which uses a MySQL database schema consisting of
the following tables: ::

	+--------------------------+
	| Tables                   |
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

See :download:`Database Schema for v3.0 (png) <_static/v3_0.png>` for a 
static diagram of the relationships between the tables.  For an
interactive look at the schema relationships install MySQL Workbench 
`MySQL Workbench <https://www.mysql.com/products/workbench/>`_,
then download and open :download:`Database Schema for v3.0 (mwb) <_static/v3_0-2.mwb>`.

Column names beginning with a lowercase character signify that the
column is inherent to the table and is not a foreign key. Column names 
beginning with an uppercase character signify that the column is a 
foreign key relationship to another table.

The descriptions of the tables below is presented roughly in order of importance
to functionality.

Input Tables
------------

**Cloud**
::

   +---------+------------+------+-----+---------+----------------+
   | Field   | Type       | Null | Key | Default | Extra          |
   +---------+------------+------+-----+---------+----------------+
   | cloudID | int(11)    | NO   | PRI | NULL    | auto_increment |
   | c_date  | bigint(20) | NO   |     | NULL    |                |
   | cloud   | double     | NO   |     | NULL    |                |
   +---------+------------+------+-----+---------+----------------+

The model for the weather is based on 10 years of cloud data 
from Cerro Tololo where four times per night a telescope operator estimated 
the cloud coverage on the sky in discrete 8ths. The column ``c_date`` is the 
time of observation in seconds since the beginning of the 10 years, and  the 
column ``cloud`` is the sky coverage fraction.  The simulator implements this 
model by selecting ``cloud`` at the time ``c_date`` which immediate precedes
the start time of a proposed observation. Observing proceeds while this 
value does not
exceed a specification in the configuration files (usually set to 0.7). If 
``cloud`` exceeds the specified value, then observing pauses for 300 seconds,
after which it is re-evaluated.

**Seeing**
::

	+----------+------------+------+-----+---------+----------------+
	| Field    | Type       | Null | Key | Default | Extra          |
	+----------+------------+------+-----+---------+----------------+
	| seeingID | int(11)    | NO   | PRI | NULL    | auto_increment |
	| s_date   | bigint(20) | NO   |     | NULL    |                |
	| seeing   | double     | NO   |     | NULL    |                |
	+----------+------------+------+-----+---------+----------------+

The seeing model is based on seeing observations taken on Cerro Pachon for a 
total of one year.  A semi-analytic technique
was applied to this data to estimate the seeing over a 10-year period of time
in intervals of 5 minutes. 
This model will be replaced with 10 years of actual seeing measurements 
on Cerro Pachon.  The column ``seeing`` is the FWHM of the atmospheric PSF 
(arcseconds) at time ``s_date`` (seconds) since the beginning of the simulations.
The simulator implements this 
model by chosing the value after the time of observation until the time of the 
next observation, and observing proceeds unless this value exceeds a 
specification in the configuration files (typically 1.5 arcsec). 

**Field**
::

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

OpSim simulates observing by "visiting" fields on the sky whose coordinates
are defined in this table.  The field centers are determined from a tesselation
(or tiling) of the celestial sphere which results in a closest-packed set of 
5280 hexagons and 12 pentagons inscribed in circular fields having a 
3.5-degree diameter (R. H. Hardin, N. J. A. Sloane and W. D. Smith, "Tables of spherical codes with icosahedral symmetry," published electronically at http://NeilSloane.com/icosahedral.codes/). These coordinates are stored in this table 
during the installation of OpSim, however, any other set of field centers may 
be substituted.  During a simulation, each configuration file (or observing 
program) specifies either a list of field centers or a region on the sky to 
observe, and these are mapped to the corresponding fields from this
table.  The column ``fieldID`` is a unique field identifier, ``fieldRA`` is the 
Right Ascension (J2000) of the field, and ``fieldDec`` is the Declination
(J2000) of the field.

Output Tables
-------------

**Session** 
::

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

This table is the hub for all OpSim runs and ties all the tables together.
Every OpSim simulation generates a ``sessionID`` and an entry in this table 
which is unique for each database.
All of the output tables 
have a foreign key relationship with this table, and output data is identified 
primarily using the ``sessionID`` column from this table.

**Config**
::

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| configID          | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
	| moduleName        | varchar(128)     | NO   |     | NULL    |                |
	| paramIndex        | int(11)          | NO   |     | NULL    |                |
	| paramName         | varchar(64)      | NO   |     | NULL    |                |
	| paramValue        | varchar(128)     | NO   |     | NULL    |                |
	| comment           | varchar(512)     | YES  |     | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	| nonPropID         | int(10)          | YES  |     | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

All of the parameters and their values from all configuration files used to
specify a simulation are stored in this table.

**Config_File**
::

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| config_fileID     | int(11)          | NO   | PRI | NULL    | auto_increment |
	| filename          | varchar(45)      | NO   |     | NULL    |                |
	| data              | blob             | NO   |     | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

This table is intended to store a complete copy of the contents of
all configuration files including commented lines. It has not yet been
implemented.

**Proposal** 
::

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

The names of all proposals ``propConf`` and their identifier ``propID`` which 
were used to drive a simulation are listed for each ``SessionID`` in this table.

**Proposal_Field** 
::

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| proposal_field_id | int(10)          | NO   | PRI | NULL    | auto_increment |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	| Proposal_propID   | int(10) unsigned | NO   | MUL | NULL    |                |
	| Field_fieldID     | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

This is a many-to-many relationship table that stores the fields ``fieldID`` 
from the Field table which were mapped to the field centers
or regions specified for each proposal ``propID``.

**ObsHistory** 
::

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

This table stores a record of each visit made by the telescope 
during a simulated survey.

**ObsHistory_Proposal** 
::

	+------------------------------+------------------+------+-----+---------+----------------+
	| Field                        | Type             | Null | Key | Default | Extra          |
	+------------------------------+------------------+------+-----+---------+----------------+
	| obsHistory_propID            | int(10)          | NO   | PRI | NULL    | auto_increment |
	| Proposal_propID              | int(10) unsigned | NO   |     | NULL    |                |
	| propRank                     | double           | NO   |     | NULL    |                |
	| ObsHistory_obsHistID         | int(10) unsigned | NO   | MUL | NULL    |                |
	| ObsHistory_Session_sessionID | int(10) unsigned | NO   |     | NULL    |                |
	+------------------------------+------------------+------+-----+---------+----------------+

This table maps visits to a field to the proposal or proposals that 
requested or required it. 

**MissedHistory**
::

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


When a sequence of visits is requested the acquired visits are recorded in the 
ObsHistory table, but if a subsequent visit in the sequence is missed - 
meaning the target
window of time for that visit has closed (or the simulation ends) - that visit 
is recorded in this table.  The time is the point at which the simulator detects
that the visit was not acquired, so it could be substantially different from 
the end of the target window of time if the night ends or weather delays
observing.
WLtype=True proposals attempt to preferentially collect visits within specific
time intervals, but the initial visit still contributes usefully to the end
goal. For this reason if a subsequent visit to a field is not acquired within 
the target window of time, it is not considered to be "missed" and will not
appear in this table.

**SeqHistory** 
::

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

The status of each sequence of visits to a field requested by a proposal is
recorded in this table, and it is populated when either the sequence has 
completed or is lost due to either missing the requested time window or the end of the simulation.
If RestartCompleteSequences = True or RestartLostSequences = True, then a
new record for the next sequence of visits to that field is created.


**SeqHistory_MissedHistory** 
::

	+---------------------------------+------------------+------+-----+---------+----------------+
	| Field                           | Type             | Null | Key | Default | Extra          |
	+---------------------------------+------------------+------+-----+---------+----------------+
	| seqhistory_missedHistID         | int(10)          | NO   | PRI | NULL    | auto_increment |
	| SeqHistory_sequenceID           | int(10) unsigned | NO   | MUL | NULL    |                |
	| MissedHistory_missedHistID      | int(10) unsigned | NO   | MUL | NULL    |                |
	| MissedHistory_Session_sessionID | int(10) unsigned | NO   |     | NULL    |                |
	+---------------------------------+------------------+------+-----+---------+----------------+

This table maps the visits to a field which were missed (in MissedHistory)
to the sequence of which it was a member (a many-to-many relationship).  


**SeqHistory_ObsHistory** 
::

	+------------------------------+------------------+------+-----+---------+----------------+
	| Field                        | Type             | Null | Key | Default | Extra          |
	+------------------------------+------------------+------+-----+---------+----------------+
	| seqhistory_obsHistID         | int(10)          | NO   | PRI | NULL    | auto_increment |
	| SeqHistory_sequenceID        | int(10) unsigned | NO   | MUL | NULL    |                |
	| ObsHistory_obsHistID         | int(10) unsigned | NO   | MUL | NULL    |                |
	| ObsHistory_Session_sessionID | int(10) unsigned | NO   |     | NULL    |                |
	+------------------------------+------------------+------+-----+---------+----------------+

This table maps visits to a field (ObsHistory_obsHistID) to the particular sequence (SeqHistory_sequenceID) for which they were acquired (a many-to-many relationship). 

**SlewActivities** 
::

	+--------------------+-------------+------+-----+---------+----------------+
	| Field              | Type        | Null | Key | Default | Extra          |
	+--------------------+-------------+------+-----+---------+----------------+
	| slewActivityID     | bigint(20)  | NO   | PRI | NULL    | auto_increment |
	| activity           | varchar(16) | NO   |     | NULL    |                |
	| actDelay           | double      | NO   |     | NULL    |                |
	| inCriticalPath     | varchar(16) | NO   |     | NULL    |                |
	| SlewHistory_slewID | bigint(20)  | NO   | MUL | NULL    |                |
	+--------------------+-------------+------+-----+---------+----------------+

This table keeps track of the various slew activities 
for a slew. 

**SlewHistory** 
::

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

This is
one-to-one relationship table between the SlewHistory table and the ObsHistory
table. It keeps track of the slew associated with each visit.

**SlewMaxSpeeds** 
::

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

This table is a one-to-one relationship table between the 
SlewHistory table and the
SlewMaxSpeeds table. This table keeps of the various speeds of the instrument
during a slew. 

**SlewState** 
::

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

This table keeps
track of the initial and the final slew states and the various instrument
parameters for a slew. 

**TimeHistory** 
::

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

This table notes the time of certain events: the start of a night (event=0), a 
new lunation or waning moon (event=1), a waxing moon (event=2), the beginning 
of a new year (event=3), the end of dusk (event=4), the beginning of dawn 
(event=5), and the end of a night (event=6).

**Log** 
::

	+-------------------+------------------+------+-----+---------+----------------+
	| Field             | Type             | Null | Key | Default | Extra          |
	+-------------------+------------------+------+-----+---------+----------------+
	| logID             | int(10)          | NO   | PRI | NULL    | auto_increment |
	| log_name          | varchar(64)      | NO   |     | NULL    |                |
	| log_value         | varchar(512)     | NO   |     | NULL    |                |
	| Session_sessionID | int(10) unsigned | NO   | MUL | NULL    |                |
	+-------------------+------------------+------+-----+---------+----------------+

This table is intended to store code level log statements to be used
primarily for debugging purposes. It has not yet been implemented.

