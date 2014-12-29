# System modules
import os
import socket
import sys
import time
import logging

# Third-party includes
import MySQLdb
from exceptions import *

class Opsim_Cloud(object):
    pass

class Opsim_Config(object):
    pass

class Opsim_Config_File(object):
    pass

class Opsim_Field(object):
    pass

class Opsim_Log(object):
    pass

class Opsim_ObsHistory(object):
    pass

class Opsim_MissedHistory(object):
    pass

class Opsim_ObsHistory_Proposal(object):
    pass

class Opsim_Proposal(object):
    pass

class Opsim_Proposal_Field(object):
    pass

class Opsim_Seeing(object):
    pass

class Opsim_SeqHistory(object):
    pass

class Opsim_SeqHistory_ObsHistory(object):
    pass

class Opsim_SeqHistory_MissedHistory(object):
    pass

class Opsim_Session(object):
    pass

class Opsim_SlewActivities(object):
    pass

class Opsim_SlewHistory(object):
    pass

class Opsim_SlewMaxSpeeds(object):
    pass

class Opsim_SlewState(object):
    pass

class Opsim_TimeHistory(object):
    pass

class Database :
    def __init__(self, dbWrite):

	self.dbWrite = dbWrite
	print "dbWrite = "
	print dbWrite

        try:
            self.DBHOST  = os.environ['DBHOST']
        except:
             self.DBHOST = 'localhost'

        try:
            self.DBPORT   = os.environ['DBPORT']
            if self.DBPORT == 'None':
                self.DBPORT = None
            else:
            	self.DBPORT = int(self.DBPORT)
        except:
            self.DBPORT   = None

        try:
            self.DBDB     = os.environ['DBDB']
        except:
            self.DBDB     = 'OpsimDB'

        try:
            self.DBUSER   = os.environ['DBUSER']
        except:
            self.DBUSER   = 'www'

        try:
            self.DBPASSWD = os.environ['DBPASSWD']
        except:
            self.DBPASSWD = 'zxcvbnm'

        done = False
        t0 = time.time ()
        timeout=10
        #print "We are going to connect to DB"
        #self.openConnection()
        while (not done):
            # Here until handling exceptions better is done.
            #self.connection = self.openConnection ()
            try:
                self.connection = self.openConnection ()
                done = True
            #print "Open connection"
            except:
                if (time.time () - t0 > timeout):
                    raise (IOError, 'Connection to the database failed.')
                else:
                    continue

    def openConnection (self):
        """
            Open a connection to DBDB running on DBHOST:DBPORT as user DBUSER
            and return the connection.

            Raise exception in case of error.
            """
        # Use configuration file with EUPS install otherwise use old way.
        conf_file = os.path.join(os.getenv("HOME"), ".my.cnf")
        if os.path.isfile(conf_file):
            self.conn = MySQLdb.connect(read_default_file=conf_file, db=self.DBDB)
        else:
            if (self.DBPORT):
                self.conn = MySQLdb.connect (user=self.DBUSER, passwd=self.DBPASSWD, db=self.DBDB, host=self.DBHOST, port=self.DBPORT)
            else:
                self.conn = MySQLdb.connect (user=self.DBUSER, passwd=self.DBPASSWD, db=self.DBDB, host=self.DBHOST)
        self.getCursor()

    def getCursor (self):
        """
            If connection is still valid, return a cursor. Otherwise
            open a new connection and return a cursor from it.

            Return a two element array with the connection and the
            cursor
            """
        try:
            self.cur = self.conn.cursor ()
        except:
            try:
                self.conn = self.openConnection ()
                self.cur = self.conn.cursor ()
            except:
                raise (IOException, 'Connection to the DB failed.')

    def executeSQL (self, query):
        """
            Execute any given query and return both the number of rows that
            were affected and the results of the query.

            Input
            query       A string containing the SQL query to be sent to the
            database.

            Return
            A two element array of the form [n, res] where:
            n       number of affected rows
            res     result array: [[col1, col2, ..], [col1, col2, ...], ...]
            If the query returns no data, res is empty.

            Raise
            Exception if either the connection to the DB failed or the
            execution of the query failed.
            """

        n = self.cur.execute (query)
        try:
            res = self.cur.fetchall ()
        except:
            res = []

        # Return the results
        return (n, res)

    def closeConnection(self) :
        # Close the cursor
        self.cur.close()
        del (self.cur)
        self.conn.close()
        del (self.conn)

    def newSession(self, sessionUser, sessionHost, sessionDate, version, runComment) :
        try:
            oSession = Opsim_Session()
            oSession.sessionUser = sessionUser
            oSession.sessionHost = sessionHost
            oSession.sessionDate = sessionDate
            oSession.version = version
            oSession.runComment = runComment
            sql = 'insert into Session (sessionUser, sessionHost, sessionDate, version, runComment) values ("%s", "%s", "%s", "%s", "%s")' % (sessionUser, sessionHost, sessionDate, version, runComment)
            (n, res) = self.executeSQL(sql)
            sql = 'select sessionID from Session where '
            sql += 'sessionUser="%s" and ' % (sessionUser)
            sql += 'sessionHost="%s" and ' % (sessionHost)
            sql += 'sessionDate="%s"' % (sessionDate)
            (n, res) = self.executeSQL (sql)
            oSession.sessionID = res[0][0]
        except:
            raise
        return oSession

    def addConfig(self, sessionID, propID, moduleName, paramIndex, paramName, paramValue, comment) :
        try:
            oConfig = Opsim_Config()
            oConfig.Session_sessionID = sessionID
            oConfig.nonPropID = propID
            oConfig.moduleName = moduleName
            oConfig.paramIndex = paramIndex
            oConfig.paramName = paramName
            oConfig.paramValue = paramValue
            oConfig.comment = comment
            sql = 'insert into Config (Session_sessionID, nonPropID, moduleName, paramIndex, paramName, paramValue, comment) values (%d, %d, "%s", %d, "%s", "%s", "%s")' % (sessionID, propID, moduleName, paramIndex, paramName, paramValue, comment)
            (n, res) = self.executeSQL (sql)
        except:
            raise

    def addTimeHistory(self, sessionID, date, mjd, nightCnt, event) :
        try:
            oTimeHistory = Opsim_TimeHistory()
            oTimeHistory.date = date
            oTimeHistory.mjd = mjd
            oTimeHistory.night = nightCnt
            oTimeHistory.event = event
            oTimeHistory.Session_sessionID = sessionID
	    if self.dbWrite:
	        sql = 'insert into TimeHistory (date, mjd, night, event, Session_sessionID) values (%d, %f, %d, %d, %d)' % (date, mjd, nightCnt, event, sessionID)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addProposal(self, propConf, propName, sessionID, objectHost, objectID) :
        try:
            oProposal = Opsim_Proposal()
            oProposal.propConf = propConf
            oProposal.propName = propName
            oProposal.Session_sessionID = sessionID
            oProposal.objectID = objectID
            oProposal.objectHost = objectHost
            sql = 'insert into Proposal (propConf, propName, Session_sessionID, objectID, objectHost) values ("%s", "%s", %d, %d, "%s")' % (propConf, propName, sessionID, objectID, objectHost)
            (n, res) = self.executeSQL(sql)

            sql = 'select propID from Proposal where '
            sql += 'propConf="%s" and ' % (propConf)
            sql += 'propName="%s" and ' % (propName)
            sql += 'Session_sessionID=%d' % (sessionID)
            (n, res) = self.executeSQL (sql)
            oProposal.propID = res[0][0]
        except:
            raise
        return oProposal

    def createOlapTable(self, overlappingField) :
        if self.dbWrite:

            sql = 'create table %s (fieldID int(10) not null, fieldFov float not null, fieldRA float not null, fieldDec float not null, fieldGL float not null, fieldGB float not null, fieldEL float not null, fieldEB float not null, constraint field_pk primary key (fieldID))' % (overlappingField)
            (n, res) = self.executeSQL(sql)
        return overlappingField

    def dropTable(self, tableName) :
        sql = 'drop table if exists %s; ' %(tableName)
        (n, res) = self.executeSQL(sql)
        return res

    def addConfigFile(self, filename, data, sessionID):
        try:
            oConfigFile = Opsim_Config_File()
            oConfigFile.filename = filename
            oConfigFile.data = data
            oConfigFile.Session_sessionID = sessionID
            sql = 'insert into ConfigFile (filename, data, Session_sessionID) values ("%s", "%s", %d)' % (filename, data, sessionID)
            (n, res) = self.executeSQL(sql)
        except:
            raise

    def addLog(self, log_name, log_value, sessionID):
        try:
            oLog = Opsim_Log()
            oLog.log_name = log_name
            oLog.log_value = log_value
            oLog.Session_sessionID = sessionID;
            if self.dbWrite:
                sql = 'insert into Log (log_name, log_value, Session_sessionID) values ("%s", "%s", %d)' % (log_name, log_value, sessionID)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addProposalField(self, sessionID, propID, fieldID):
        try:
            oPropField = Opsim_Proposal_Field()
            oPropField.Session_sessionID = sessionID
            oPropField.Proposal_propID = propID
            oPropField.Field_fieldID = fieldID
            if self.dbWrite:
                sql = 'insert into Proposal_Field (Session_sessionID, Proposal_propID, Field_fieldID) values (%d, %d, %d)' % (sessionID, propID, fieldID)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addSeqHistory(self, startDate, expDate, seqnNum, completion, reqEvents, actualEvents,
                      endStatus, parent_sequenceID, fieldID, sessionID, propID):
        try:
            oSeqHistory = Opsim_SeqHistory()
            oSeqHistory.startDate = startDate
            oSeqHistory.expDate = expDate
            oSeqHistory.seqnNum = seqnNum
            oSeqHistory.completion = completion
            oSeqHistory.reqEvents = reqEvents
            oSeqHistory.actualEvents = actualEvents
            oSeqHistory.endStatus = endStatus
            oSeqHistory.parent_sequenceID = parent_sequenceID
            oSeqHistory.Field_fieldID = fieldID
            oSeqHistory.Session_sessionID = sessionID
            oSeqHistory.Proposal_propID = propID
            if self.dbWrite:
                sql = 'insert into SeqHistory (startDate, expDate, seqnNum, completion, reqEvents, actualEvents, endStatus, parent_sequenceID, Field_fieldID, Session_sessionID, Proposal_propID) values (%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)' % (startDate, expDate, seqnNum, completion, reqEvents, actualEvents, endStatus, parent_sequenceID, fieldID, sessionID, propID)
                (n, res) = self.executeSQL(sql)

                sql = 'select sequenceID from SeqHistory where '
                sql += 'startDate=%d and ' % (startDate)
                sql += 'expDate=%d and ' % (expDate)
                sql += 'Field_fieldID=%d and ' % (fieldID)
                sql += 'Session_sessionID=%d and ' % (sessionID)
                sql += 'Proposal_propID=%d' % (propID)
                (n, res) = self.executeSQL (sql)
                oSeqHistory.sequenceID = res[0][0]
	    else:
		oSeqHistory.sequenceID = 0
        except:
            raise
        return oSeqHistory

    def addSeqHistoryObsHistory(self, sequenceID, obsHistID, sessionID):
        try:
            oSeqHistoryObsHistory = Opsim_SeqHistory_ObsHistory()
            oSeqHistoryObsHistory.SeqHistory_sequenceID = sequenceID
            oSeqHistoryObsHistory.ObsHistory_obsHistID = obsHistID
            oSeqHistoryObsHistory.ObsHistory_Session_sessionID = sessionID
            if self.dbWrite:
                sql = 'insert into SeqHistory_ObsHistory (SeqHistory_sequenceID, ObsHistory_obsHistID, ObsHistory_Session_sessionID) values (%d, %d, %d)' % (sequenceID, obsHistID, sessionID)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addSeqHistoryMissedHistory(self, sequenceID, missedHistID, sessionID):
        try:
            oSeqHistoryMissedHistory = Opsim_SeqHistory_MissedHistory()
            oSeqHistoryMissedHistory.SeqHistory_sequenceID = sequenceID
            oSeqHistoryMissedHistory.MissedHistory_missedHistID = missedHistID
            oSeqHistoryMissedHistory.MissedHistory_Session_sessionID = sessionID
            if self.dbWrite:
                sql = 'insert into SeqHistory_MissedHistory (SeqHistory_sequenceID, MissedHistory_missedHistID, MissedHistory_Session_sessionID) values (%d, %d, %d)' % (sequenceID, missedHistID, sessionID)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addObsHistoryProposal(self, propID, obsHistID, sessionID, propRank):
        try:
            oObsHistoryProposal = Opsim_ObsHistory_Proposal()
            oObsHistoryProposal.Proposal_propID = propID
            oObsHistoryProposal.ObsHistory_obsHistID = obsHistID
            oObsHistoryProposal.ObsHistory_Session_sessionID = sessionID
            oObsHistoryProposal.propRank = propRank
            if self.dbWrite:
                sql = 'insert into ObsHistory_Proposal (Proposal_propID, ObsHistory_obsHistID, ObsHistory_Session_sessionID, propRank) values (%d, %d, %d, %f)' % (propID, obsHistID, sessionID, propRank)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addMissedObservation(self, filter, expDate, expMJD, night, lst, sessionID, fieldID):
        try:
            oMissed = Opsim_MissedHistory()
            oMissed.filter = filter
            oMissed.expDate = expDate
            oMissed.expMJD = expMJD
            oMissed.night = night
            oMissed.lst = lst
            oMissed.Session_sessionID = sessionID
            oMissed.Field_fieldID = fieldID
            if self.dbWrite:
                sql = 'insert into MissedHistory (filter, expDate, expMJD, night, lst, Session_sessionID, Field_fieldID) values ("%s", %d, %f, %d, %f, %d, %d)' % (filter, expDate, expMJD, night, lst, sessionID, fieldID)
                (n, res) = self.executeSQL(sql)

                sql = 'select missedHistID from MissedHistory where '
                sql += 'filter="%s" and ' % (filter)
                sql += 'expDate=%d and ' % (expDate)
                sql += 'Field_fieldID=%d and ' % (fieldID)
                sql += 'Session_sessionID=%d' % (sessionID)
                (n, res) = self.executeSQL (sql)
                oMissed.missedHistID = res[0][0]
	    else:
		oMissed.missedHistID = 0
        except:
            raise
        return oMissed

    def addObservation(self, obsHistID, filter, expDate, expMJD, night, visitTime, visitExpTime, finRank,
                       finSeeing, transparency, airmass, vSkyBright, filtSkyBright, rotSkyPos,
                       lst, alt, az, dist2Moon, solarElong, moonRA, moonDec, moonAlt, moonAZ,
                       moonPhase, sunAlt, sunAZ, phaseAngle, rScatter, mieScatter, moonIllum,
                       moonBright, darkBright, rawSeeing, wind, humidity, sessionID, fieldID):
        # visitTime and visitExpTime are switched here to correct their incorrect use elsewhere. There are 
        # too many places where visitExpTime (seen as 34 in the code and DB) are used to make changes in the 
        # code. visitTime (which is seen as zero in the code and DB) will be made to be 30 in the Observation 
        # class since it is never used anywhere else in the code.
        try:
            oObs = Opsim_ObsHistory()
            oObs.obsHistID = obsHistID
            oObs.filter = filter
            oObs.expDate = expDate
            oObs.expMJD = expMJD
            oObs.night = night
            oObs.visitTime = visitExpTime
            oObs.visitExpTime = visitTime
            oObs.finRank = finRank
            oObs.finSeeing = finSeeing
            oObs.transparency = transparency
            oObs.airmass = airmass
            oObs.vSkyBright = vSkyBright
            oObs.filtSkyBright = filtSkyBright
            oObs.rotSkyPos = rotSkyPos
            oObs.lst = lst
            oObs.alt = alt
            oObs.az = az
            oObs.dist2Moon = dist2Moon
            oObs.solarElong = solarElong
            oObs.moonRA = moonRA
            oObs.moonDec = moonDec
            oObs.moonAlt = moonAlt
            oObs.moonAZ = moonAZ
            oObs.moonPhase = moonPhase
            oObs.sunAlt = sunAlt
            oObs.sunAZ = sunAZ
            oObs.phaseAngle = phaseAngle
            oObs.rScatter = rScatter
            oObs.mieScatter = mieScatter
            oObs.moonIllum = moonIllum
            oObs.moonBright = moonBright
            oObs.darkBright = darkBright
            oObs.rawSeeing = rawSeeing
            oObs.wind = wind
            oObs.humidity = humidity
            oObs.Session_sessionID = sessionID
            oObs.Field_fieldID = fieldID
            if self.dbWrite:
                sql = 'insert into ObsHistory (obsHistID, filter, expDate, expMJD, night, visitTime, visitExpTime, finRank, finSeeing, transparency, airmass, vSkyBright, filtSkyBright, rotSkyPos, lst, alt, az, dist2Moon, solarElong, moonRA, moonDec, moonAlt, moonAZ, moonPhase, sunAlt, sunAZ, phaseAngle, rScatter, mieScatter, moonIllum, moonBright, darkBright, rawSeeing, wind, humidity, Session_sessionID, Field_fieldID) values (%d, "%s", %d, %f, %d, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %d, %d)' % (obsHistID, filter, expDate, expMJD, night, visitExpTime, visitTime, finRank, finSeeing, transparency, airmass, vSkyBright, filtSkyBright, rotSkyPos, lst, alt, az, dist2Moon, solarElong, moonRA, moonDec, moonAlt, moonAZ, moonPhase, sunAlt, sunAZ, phaseAngle, rScatter, mieScatter, moonIllum, moonBright, darkBright, rawSeeing, wind, humidity, sessionID, fieldID)
                (n, res) = self.executeSQL(sql)
        except:
            raise
        return oObs

    def addSlewHistory(self, slewCount, startDate, endDate, slewTime, slewDist, obsHistID, sessionID):
        try:
            oSlewHist = Opsim_SlewHistory()
            oSlewHist.slewCount = slewCount
            oSlewHist.startDate = startDate
            oSlewHist.endDate = endDate
            oSlewHist.slewTime = slewTime
            oSlewHist.slewDist = slewDist
            oSlewHist.ObsHistory_obsHistID = obsHistID
            oSlewHist.ObsHistory_Session_sessionID = sessionID
            if self.dbWrite:
                sql = 'insert into SlewHistory (slewCount, startDate, endDate, slewTime, slewDist, ObsHistory_obsHistID, ObsHistory_Session_sessionID) values (%d, %f, %f, %f, %f, %d, %d)' % (slewCount, startDate, endDate, slewTime, slewDist, obsHistID, sessionID)
                (n, res) = self.executeSQL(sql)

                sql = 'select slewID from SlewHistory where '
                sql += 'ObsHistory_obsHistID=%d and ' % (obsHistID)
                sql += 'ObsHistory_Session_sessionID=%d' % (sessionID)
                (n, res) = self.executeSQL (sql)
                oSlewHist.slewID = res[0][0]
	    else:
		oSlewHist.slewID = 0
        except:
            raise
        return oSlewHist

    def addSlewActivities(self, activity, actDelay, inCriticalPath, slewID):
        try:
            oSlewAct = Opsim_SlewActivities()
            oSlewAct.activity = activity
            oSlewAct.actDelay = actDelay
            oSlewAct.inCriticalPath = inCriticalPath
            oSlewAct.SlewHistory_slewID = slewID
            if self.dbWrite:
                sql = 'insert into SlewActivities (activity, actDelay, inCriticalPath, SlewHistory_slewID) values ("%s", %f, "%s", %d)' % (activity, actDelay, inCriticalPath, slewID)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addSlewMaxSpeeds(self, domAltSpd, domAzSpd, telAltSpd, telAzSpd, rotSpd, slewID):
        try:
            oSlewMaxSpeed = Opsim_SlewMaxSpeeds()
            oSlewMaxSpeed.domAltSpd = domAltSpd
            oSlewMaxSpeed.domAzSpd = domAzSpd
            oSlewMaxSpeed.telAltSpd = telAltSpd
            oSlewMaxSpeed.telAzSpd = telAzSpd
            oSlewMaxSpeed.rotSpd = rotSpd
            oSlewMaxSpeed.SlewHistory_slewID = slewID
            if self.dbWrite:
                sql = 'insert into SlewMaxSpeeds (domAltSpd, domAzSpd, telAltSpd, telAzSpd, rotSpd, SlewHistory_slewID) values (%f, %f, %f, %f, %f, %d)' % (domAltSpd, domAzSpd, telAltSpd, telAzSpd, rotSpd, slewID)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addSlewState(self, slewStateDate, tra, tdec, tracking, alt, az, pa, domAlt,
                     domAz, telAlt, telAz, rotTelPos, filter, state, slewID):
        try:
            oSlewState = Opsim_SlewState()
            oSlewState.slewStateDate = slewStateDate
            oSlewState.tra = tra
            oSlewState.tdec = tdec
            oSlewState.tracking = tracking
            oSlewState.alt = alt
            oSlewState.az = az
            oSlewState.pa = pa
            oSlewState.domAlt = domAlt
            oSlewState.domAz = domAz
            oSlewState.telAlt = telAlt
            oSlewState.telAz = telAz
            oSlewState.rotTelPos = rotTelPos
            oSlewState.filter = filter
            oSlewState.state = state
            oSlewState.SlewHistory_slewID = slewID
            if self.dbWrite:
                sql = 'insert into SlewState (slewStateDate, tra, tdec, tracking, alt, az, pa, domAlt, domAz, telAlt, telAz, rotTelPos, filter, state, SlewHistory_slewID) values (%f, %f, %f, "%s", %f, %f, %f, %f, %f, %f, %f, %f, "%s", %d, %d)' % (slewStateDate, tra, tdec, tracking, alt, az, pa, domAlt, domAz, telAlt, telAz, rotTelPos, filter, state, slewID)
                (n, res) = self.executeSQL(sql)
        except:
            raise

    def addOlap(self, olapTable, id, fov, ra, dec, gl, gb, el, eb) :
        if self.dbWrite:
            sql = 'insert into %s (fieldID, fieldFov, fieldRA, fieldDec, fieldGL, fieldGB, fieldEL, fieldEB) values (%d, %f, %f, %f, %f, %f, %f, %f)' % (olapTable, id, fov, ra, dec, gl, gb, el, eb)
            (n, res) = self.executeSQL(sql)

if __name__ == "__main__":
    db = Database(True)
