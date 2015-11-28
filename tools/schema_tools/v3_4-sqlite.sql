CREATE TABLE Session (sessionID INTEGER PRIMARY KEY, sessionUser TEXT, sessionHost TEXT, sessionDate TEXT, version TEXT, runComment TEXT);
CREATE INDEX s_host_user_date_idx ON Session(sessionUser, sessionHost, sessionDate);

CREATE TABLE Config (configID INTEGER PRIMARY KEY, moduleName TEXT, paramIndex INTEGER, paramName TEXT, paramValue TEXT, comment TEXT, Session_sessionID INTEGER, nonPropID INTEGER);
CREATE INDEX fk_config_session_idx ON Config(Session_sessionID);

CREATE TABLE Field (fieldID INTEGER PRIMARY KEY, fieldFov REAL, fieldRA REAL, fieldDec REAL, fieldGL REAL, fieldGB REAL, fieldEL REAL, fieldEB REAL);

CREATE TABLE ObsHistory (obsHistID INTEGER PRIMARY KEY, Session_sessionID INTEGER, filter TEXT, expDate INTEGER, expMJD REAL, night INTEGER, visitTime REAL, visitExpTime REAL, finRank REAL, finSeeing REAL, transparency REAL, airmass REAL, vSkyBright REAL, filtSkyBrightness REAL, rotSkyPos REAL, lst REAL, altitude REAL, azimuth REAL, dist2Moon REAL, solarElong REAL, moonRA REAL, moonDec REAL, moonAlt REAL, moonAZ REAL, moonPhase REAL, sunAlt REAL, sunAZ REAL, phaseAngle REAL, rScatter REAL, mieScatter REAL, moonIllum REAL, moonBright REAL, darkBright REAL, rawSeeing REAL, wind REAL, humidity REAL, fiveSigmaDepth REAL, ditheredRA REAL, ditheredDec REAL, Field_fieldID INTEGER);
CREATE INDEX oh_field_filter_idx ON ObsHistory(filter);
CREATE INDEX fk_ObsHistory_Session_idx ON ObsHistory(Session_sessionID);
CREATE INDEX fk_ObsHistory_field_idx ON ObsHistory(Field_fieldID);

CREATE TABLE Proposal (propID INTEGER PRIMARY KEY, propConf TEXT, propName TEXT, objectID INTEGER, objectHost TEXT, Session_sessionID INTEGER);
CREATE INDEX fk_Proposal_Session_idx ON Proposal(Session_sessionID);

CREATE TABLE SeqHistory (sequenceID INTEGER PRIMARY KEY, startDate INTEGER, expDate INTEGER, seqnNum INTEGER, completion REAL, reqEvents INTEGER, actualEvents INTEGER, endStatus INTEGER, parent_sequenceID INTEGER, Field_fieldID INTEGER, Session_sessionID INTEGER, Proposal_propID INTEGER);
CREATE INDEX fk_SeqHistory_Field_idx ON SeqHistory(Field_fieldID);
CREATE INDEX fk_SeqHistory_Session_idx ON SeqHistory(Session_sessionID);
CREATE INDEX fk_SeqHistory_Proposal_idx ON SeqHistory(Proposal_propID);

CREATE TABLE SlewHistory (slewID INTEGER PRIMARY KEY, slewCount INTEGER, startDate REAL, endDate REAL, slewTime REAL, slewDist REAL, ObsHistory_obsHistID INTEGER, ObsHistory_Session_sessionID INTEGER);
CREATE INDEX fk_SlewHistory_ObsHistory_idx ON SlewHistory(ObsHistory_obsHistID, ObsHistory_Session_sessionID);

CREATE TABLE SlewActivities (slewActivityID INTEGER PRIMARY KEY, activity TEXT, actDelay REAL, inCriticalPath TEXT, SlewHistory_slewID INTEGER);
CREATE INDEX fk_SlewActivities_SlewHistory_idx ON SlewActivities(SlewHistory_slewID);

CREATE TABLE SlewState (slewIniStatID INTEGER PRIMARY KEY, slewStateDate REAL, tra REAL, tdec REAL, tracking TEXT, alt REAL, az REAL, pa REAL, domAlt REAL, domAz REAL, telAlt REAL, telAz REAL, rotTelPos REAL, filter TEXT, state INTEGER, SlewHistory_slewID INTEGER);
CREATE INDEX fk_SlewState_SlewHistory_idx ON SlewState(SlewHistory_slewID);

CREATE TABLE SlewMaxSpeeds (slewMaxSpeedID INTEGER PRIMARY KEY, domAltSpd REAL, domAzSpd REAL, telAltSpd REAL, telAzSpd REAL, rotSpd REAL, SlewHistory_slewID INTEGER);
CREATE INDEX fk_SlewMaxSpeeds_SlewHistory_idx ON SlewMaxSpeeds(SlewHistory_slewID);

CREATE TABLE TimeHistory (timeHistID INTEGER PRIMARY KEY, date INTEGER, mjd REAL, night INTEGER, event INTEGER, Session_sessionID INTEGER);
CREATE INDEX th_event_idx ON TimeHistory(event);
CREATE INDEX fk_TimeHistory_Session_idx ON TimeHistory(Session_sessionID);

CREATE TABLE ObsHistory_Proposal (obsHistory_propID INTEGER PRIMARY KEY, Proposal_propID INTEGER, propRank REAL, ObsHistory_obsHistID INTEGER, ObsHistory_Session_sessionID INTEGER);
CREATE INDEX fk_ObsHistory_Proposal_ObsHistory_idx ON ObsHistory_Proposal(ObsHistory_obsHistID, ObsHistory_Session_sessionID);

CREATE TABLE Cloud (cloudID INTEGER PRIMARY KEY, c_date INTEGER, cloud REAL);

CREATE TABLE Seeing (seeingID INTEGER PRIMARY KEY, s_date INTEGER, seeing REAL);

CREATE TABLE Log (logID INTEGER PRIMARY KEY, log_name TEXT, log_value TEXT, Session_sessionID INTEGER);
CREATE INDEX fk_Log_Session_idx ON Log(Session_sessionID);

CREATE TABLE Config_File (config_fileID INTEGER PRIMARY KEY, filename TEXT, data TEXT, Session_sessionID INTEGER);
CREATE INDEX fk_Config_File_Session_idx ON Config_File(Session_sessionID);

CREATE TABLE Proposal_Field (proposal_field_id INTEGER PRIMARY KEY, Session_sessionID INTEGER, Proposal_propID INTEGER, Field_fieldID INTEGER);
CREATE INDEX fk_Proposal_Field_Session_idx ON Proposal_Field(Session_sessionID);
CREATE INDEX fk_Proposal_Field_Proposal_idx ON Proposal_Field(Proposal_propID);
CREATE INDEX fk_Proposal_Field_Field_idx ON Proposal_Field(Field_fieldID);

CREATE TABLE SeqHistory_ObsHistory (seqhistory_obsHistID INTEGER PRIMARY KEY, SeqHistory_sequenceID INTEGER, ObsHistory_obsHistID INTEGER, ObsHistory_Session_sessionID INTEGER);
CREATE INDEX fk_SeqHistory_ObsHistory_SeqHistory_idx ON SeqHistory_ObsHistory(SeqHistory_sequenceID);
CREATE INDEX fk_SeqHistory_ObsHistory_ObsHistory_idx ON SeqHistory_ObsHistory(ObsHistory_obsHistID, ObsHistory_Session_sessionID);

CREATE TABLE MissedHistory (missedHistID INTEGER PRIMARY KEY, Session_sessionID INTEGER, filter TEXT, expDate INTEGER, expMJD REAL, night INTEGER, lst REAL, Field_fieldID INTEGER);
CREATE INDEX mh_field_filter_idx ON MissedHistory(filter);
CREATE INDEX fk_MissedHistory_Session_idx ON MissedHistory(Session_sessionID);
CREATE INDEX fk_MissedHistory_Field_idx ON MissedHistory(Field_fieldID);

CREATE TABLE SeqHistory_MissedHistory (seqhistory_missedHistID INTEGER PRIMARY KEY, SeqHistory_sequenceID INTEGER, MissedHistory_missedHistID INTEGER, MissedHistory_Session_sessionID INTEGER);
CREATE INDEX fk_SeqHistory_MissedHistory_SeqHistory_idx ON SeqHistory_MissedHistory(SeqHistory_sequenceID);
CREATE INDEX fk_SeqHistory_MissedHistory_ObsHistory_idx ON SeqHistory_MissedHistory(MissedHistory_missedHistID, MissedHistory_Session_sessionID);

CREATE TABLE Summary (obsHistID INTEGER, sessionID INTEGER, propID INTEGER, fieldID INTEGER, fieldRA REAL, fieldDec REAL, filter TEXT, expDate INTEGER, expMJD REAL, night INTEGER, visitTime REAL, visitExpTime REAL, finRank REAL, FWHMeff REAL, FWHMgeom REAL, transparency REAL, airmass REAL, vSkyBright REAL, filtSkyBrightness REAL, rotSkyPos REAL, rotTelPos REAL, lst REAL, altitude REAL, azimuth REAL, dist2Moon REAL, solarElong REAL, moonRA REAL, moonDec REAL, moonAlt REAL, moonAZ REAL, moonPhase REAL, sunAlt REAL, sunAz REAL, phaseAngle REAL, rScatter REAL, mieScatter REAL, moonIllum REAL, moonBright REAL, darkBright REAL, rawSeeing REAL, wind REAL, humidity REAL, slewDist REAL, slewTime REAL, fiveSigmaDepth REAL, ditheredRA REAL, ditheredDec REAL);
CREATE INDEX fieldID_idx ON Summary(fieldID);
CREATE INDEX expMJD_idx ON Summary(expMJD);
CREATE INDEX filter_idx ON Summary(filter);
CREATE INDEX fieldRA_idx ON Summary(fieldRA);
CREATE INDEX fieldDec_idx ON Summary(fieldDec);
CREATE INDEX fieldRADec_idx ON Summary(fieldRA, fieldDec);
CREATE INDEX night_idx ON Summary(night);
CREATE INDEX propID_idx ON Summary(propID);
CREATE INDEX ditheredRA_idx ON Summary(ditheredRA);
CREATE INDEX ditheredDec_idx ON Summary(ditheredDec);
CREATE INDEX ditheredRADec_idx ON Summary(ditheredRA, ditheredDec);
CREATE INDEX filter_propID_idx ON Summary(filter, propID);

PRAGMA synchronous=off;
