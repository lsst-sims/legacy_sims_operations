from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import text

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
    def __init__(self):
        self.engine = create_engine('mysql://www:zxcvbnm@localhost/OpsimDB', echo=False)
        self.metadata = MetaData(self.engine)

        self.opsim_cloud = Table('Cloud', self.metadata, autoload=True)
        mapper(Opsim_Cloud, self.opsim_cloud)
        
        self.opsim_config = Table('Config', self.metadata, autoload=True)
        mapper(Opsim_Config, self.opsim_config)

        self.opsim_config_file = Table('Config_File', self.metadata, autoload=True)
        mapper(Opsim_Config_File, self.opsim_config_file)
        
        self.opsim_field = Table('Field', self.metadata, autoload=True)
        mapper(Opsim_Field, self.opsim_field)
        
        self.opsim_log = Table('Log', self.metadata, autoload=True)
        mapper(Opsim_Log, self.opsim_log)
        
        self.opsim_obshistory = Table('ObsHistory', self.metadata, autoload=True)
        mapper(Opsim_ObsHistory, self.opsim_obshistory)				

        self.opsim_missedhistory = Table('MissedHistory', self.metadata, autoload=True)
        mapper(Opsim_MissedHistory, self.opsim_missedhistory)				
       
        self.opsim_obshistory_proposal = Table('ObsHistory_Proposal', self.metadata, autoload=True)
        mapper(Opsim_ObsHistory_Proposal, self.opsim_obshistory_proposal)
        
        self.opsim_proposal = Table('Proposal', self.metadata, autoload=True)
        mapper(Opsim_Proposal, self.opsim_proposal)

        self.opsim_proposal_field = Table('Proposal_Field', self.metadata, autoload=True)
        mapper(Opsim_Proposal_Field, self.opsim_proposal_field)
        
        self.opsim_seeing = Table('Seeing', self.metadata, autoload=True)
        mapper(Opsim_Seeing, self.opsim_seeing)
        
        self.opsim_seqhistory = Table('SeqHistory', self.metadata, autoload=True)
        mapper(Opsim_SeqHistory, self.opsim_seqhistory)

        self.opsim_seqhistory_obshistory = Table('SeqHistory_ObsHistory', self.metadata, autoload=True)
        mapper(Opsim_SeqHistory_ObsHistory, self.opsim_seqhistory_obshistory)

        self.opsim_seqhistory_missedhistory = Table('SeqHistory_MissedHistory', self.metadata, autoload=True)
        mapper(Opsim_SeqHistory_MissedHistory, self.opsim_seqhistory_missedhistory)

        self.opsim_session = Table('Session', self.metadata, autoload=True)
        mapper(Opsim_Session, self.opsim_session)
        
        self.opsim_slewactivities = Table('SlewActivities', self.metadata, autoload=True)
        mapper(Opsim_SlewActivities, self.opsim_slewactivities)
        
        self.opsim_slewhistory = Table('SlewHistory', self.metadata, autoload=True)
        mapper(Opsim_SlewHistory, self.opsim_slewhistory)
        
        self.opsim_slewmaxspeeds = Table('SlewMaxSpeeds', self.metadata, autoload=True)
        mapper(Opsim_SlewMaxSpeeds, self.opsim_slewmaxspeeds)
        
        self.opsim_slewstate = Table('SlewState', self.metadata, autoload=True)
        mapper(Opsim_SlewState, self.opsim_slewstate)
        
        self.opsim_timehistory = Table('TimeHistory', self.metadata, autoload=True)
        mapper(Opsim_TimeHistory, self.opsim_timehistory)

        Session = sessionmaker(bind=self.engine)
        self.dbSession = Session()

    def newSession(self, sessionUser, sessionHost, sessionDate, version, runComment) :
        try:
            oSession = Opsim_Session()
            oSession.sessionUser = sessionUser
            oSession.sessionHost = sessionHost
            oSession.sessionDate = sessionDate
            oSession.version = version
            oSession.runComment = runComment
            self.dbSession.add(oSession)
            self.dbSession.commit()
            self.dbSession.refresh(oSession)
        except:
            self.dbSession.rollback()
            raise
        return oSession

    def addConfig(self, sessionID, moduleName, paramIndex, paramName, paramValue, comment) :
        try:
            oConfig = Opsim_Config()
            oConfig.Session_sessionID = sessionID
            oConfig.moduleName = moduleName
            oConfig.paramIndex = paramIndex
            oConfig.paramName = paramName
            oConfig.paramValue = paramValue
            oConfig.comment = comment
            self.dbSession.add(oConfig)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise
    
    def addTimeHistory(self, sessionID, date, mjd, nightCnt, event) :
        try:
            oTimeHistory = Opsim_TimeHistory()
            oTimeHistory.date = date
            oTimeHistory.mjd = mjd
            oTimeHistory.night = nightCnt
            oTimeHistory.event = event
            oTimeHistory.Session_sessionID = sessionID
            self.dbSession.add(oTimeHistory)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addProposal(self, propConf, propName, sessionID, objectID, objectHost) :
        try:
            oProposal = Opsim_Proposal()
            oProposal.propConf = propConf
            oProposal.propName = propName
            oProposal.Session_sessionID = sessionID
            oProposal.objectID = objectID
            oProposal.objectHost = objectHost
            self.dbSession.add(oProposal)
            self.dbSession.commit()
            self.dbSession.refresh(oProposal)
        except:
            self.dbSession.rollback()
            raise
        return oProposal

    def createOlapTable(self, overlappingField) :
        olapTable = Table(overlappingField, self.metadata,
                          Column('fieldID', Integer, nullable=False, primary_key=True, autoincrement=False),
                          Column('fieldFov', Float, nullable=False),
                          Column('fieldRA', Float, nullable=False),
                          Column('fieldDec', Float, nullable=False),
                          Column('fieldGL', Float, nullable=False),
                          Column('fieldGB', Float, nullable=False),
                          Column('fieldEL', Float, nullable=False),
                          Column('fieldEB', Float, nullable=False))
        self.metadata.create_all()
        return olapTable

    def dropTable(self, tableName) :
        conn = self.engine.connect()
        sql = 'drop table if exists %s; ' %(tableName)
        sText = text(sql)
        result = conn.execute(sText)
        return result
	
    def addConfigFile(self, filename, data, sessionID):
        try:
            oConfigFile = Opsim_Config_File()
            oConfigFile.filename = filename
            oConfigFile.data = data
            oConfigFile.Session_sessionID = sessionID
            self.dbSession.add(oConfigFile)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addLog(self, log_name, log_value, sessionID):
        try:
            oLog = Opsim_Log()
            oLog.log_name = log_name
            oLog.log_value = log_value
            oLog.Session_sessionID = sessionID;
            self.dbSession.add(oLog)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addProposalField(self, sessionID, propID, fieldID):
        try:
            oPropField = Opsim_Proposal_Field()
            oPropField.Session_sessionID = sessionID
            oPropField.Proposal_propID = propID
            oPropField.Field_fieldID = fieldID
            self.dbSession.add(oPropField)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
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
            self.dbSession.add(oSeqHistory)
            self.dbSession.commit()
            self.dbSession.refresh(oSeqHistory)
        except:
            self.dbSession.rollback()
            raise
        return oSeqHistory

    def addSeqHistoryObsHistory(self, sequenceID, obsHistID, sessionID):
        try:
            oSeqHistoryObsHistory = Opsim_SeqHistory_ObsHistory()
            oSeqHistoryObsHistory.SeqHistory_sequenceID = sequenceID
            oSeqHistoryObsHistory.ObsHistory_obsHistID = obsHistID
            oSeqHistoryObsHistory.ObsHistory_Session_sessionID = sessionID
            self.dbSession.add(oSeqHistoryObsHistory)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addSeqHistoryMissedHistory(self, sequenceID, missedHistID, sessionID):
        try:
            oSeqHistoryMissedHistory = Opsim_SeqHistory_MissedHistory()
            oSeqHistoryMissedHistory.SeqHistory_sequenceID = sequenceID
            oSeqHistoryMissedHistory.MissedHistory_missedHistID = missedHistID
            oSeqHistoryMissedHistory.MissedHistory_Session_sessionID = sessionID
            self.dbSession.add(oSeqHistoryMissedHistory)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addObsHistoryProposal(self, propID, obsHistID, sessionID, propRank):
        try:
            oObsHistoryProposal = Opsim_ObsHistory_Proposal()
            oObsHistoryProposal.Proposal_propID = propID
            oObsHistoryProposal.ObsHistory_obsHistID = obsHistID
            oObsHistoryProposal.ObsHistory_Session_sessionID = sessionID
            oObsHistoryProposal.propRank = propRank
            self.dbSession.add(oObsHistoryProposal)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
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
            self.dbSession.add(oMissed)
            self.dbSession.commit()
            self.dbSession.refresh(oMissed)
        except:
            self.dbSEssion.rollback()
            raise
        return oMissed

    def addObservation(self, obsHistID, filter, expDate, expMJD, night, visitTime, visitExpTime, finRank,
                       finSeeing, transparency, airmass, vSkyBright, filtSkyBright, rotSkyPos,
                       lst, alt, az, dist2Moon, solarElong, moonRA, moonDec, moonAlt, moonAZ,
                       moonPhase, sunAlt, sunAZ, phaseAngle, rScatter, mieScatter, moonIllum,
                       moonBright, darkBright, rawSeeing, wind, humidity, sessionID, fieldID):
        try:
            oObs = Opsim_ObsHistory()
            oObs.obsHistID = obsHistID
            oObs.filter = filter
            oObs.expDate = expDate
            oObs.expMJD = expMJD
            oObs.night = night
            oObs.visitTime = visitTime
            oObs.visitExpTime = visitExpTime
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
            self.dbSession.add(oObs)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
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
            self.dbSession.add(oSlewHist)
            self.dbSession.commit()
            self.dbSession.refresh(oSlewHist)
        except:
            self.dbSession.rollback()
            raise
        return oSlewHist

    def addSlewActivities(self, activity, actDelay, inCriticalPath, slewID):
        try:
            oSlewAct = Opsim_SlewActivities()
            oSlewAct.activity = activity
            oSlewAct.actDelay = actDelay
            oSlewAct.inCriticalPath = inCriticalPath
            oSlewAct.SlewHistory_slewID = slewID
            self.dbSession.add(oSlewAct)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
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
            self.dbSession.add(oSlewMaxSpeed)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
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
            self.dbSession.add(oSlewState)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addOlap(self, olapTable, id, fov, ra, dec, gl, gb, el, eb) :
        ins = olapTable.insert().values(fieldID=id, fieldFov=fov, fieldRA=ra, fieldDec=dec, fieldGL=gl, fieldGB=gb, fieldEL=el, fieldEB=eb)
        conn = self.engine.connect()
        conn.execute(ins)

    def executeSQL(self, sql) :
        conn = self.engine.connect()
        sText = text(sql)
        result = conn.execute(sText)
        n = result.rowcount
        res = result.fetchall()
        return (n, res)

if __name__ == "__main__":
    db = Database()
