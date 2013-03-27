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

class Opsim_AstronomicalSky(object):
    pass

class Opsim_Atmosphere(object):
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
        
        self.opsim_astronomicalsky = Table('AstronomicalSky', self.metadata, autoload=True)
        mapper(Opsim_AstronomicalSky, self.opsim_astronomicalsky)
        
        self.opsim_atmosphere = Table('Atmosphere', self.metadata, autoload=True)
        mapper(Opsim_Atmosphere, self.opsim_atmosphere)
        
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
            oConfig.session_sessionID = sessionID
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
            oTimeHistory.MJD = mjd
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
            oProposal.sessionID = sessionID
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

    def addConfigFile(self, filename, data, sessionID):
        try:
            oConfigFile = Opsim_Config_File()
            oConfigFile.filename = filename
            oConfigFile.data = data
            oConfigFile.session_sessionID = sessionID
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

    def addSeqHistoryObsHistory(self, sequenceID, obsHistID):
        try:
            oSeqHistoryObsHistory = Opsim_SeqHistory_ObsHistory()
            oSeqHistoryObsHistory.SeqHistory_sequenceID = sequenceID
            oSeqHistoryObsHistory.ObsHistory_obsHistID = obsHistID
            self.dbSession.add(oSeqHistoryObsHistory)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addObsHistoryProposal(self, propID, obsHistID, propRank):
        try:
            oObsHistoryProposal = Opsim_ObsHistory_Proposal
            oObsHistoryProposal.Proposal_propID = propID
            oObsHistoryProposal.Obshistory_obsHistID = obsHistID
            oObsHistoryProposal.propRank = propRank
            self.dbSession.add(oObsHistoryProposal)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addObservation(self, filter, expDate, expMJD, night, visitTime, visitExpTime, finRank,
                       finSeeing, transparency, airmass, vSkyBright, filtSkyBright, rotSkyPos,
                       lst, alt, az, dist2Moon, solarElong, obsType, sessionID, fieldID):
        try:
            oObs = Opsim_ObsHistory()
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
            oObs.obsType = obsType
            oObs.Session_sessionID = sessionID
            oObs.Field_fieldID = fieldID
            self.dbSession.add(oObs)
            self.dbSession.commit()
            self.dbSession.refresh(oObs)
        except:
            self.dbSession.rollback()
            raise
        return oObs

    def addAstronomicalSky(self, moonRA, moonDec, moonAlt, moonAZ, moonPhase, sunAlt, sunAZ, phaseAngle,
                           rScatter, mieScatter, moonIllum, moonBright, darkBright, obsHistID):
        try:
            oAstroSky = Opsim_AstronomicalSky()
            oAstroSky.moonRA = moonRA
            oAstroSky.moonDec = moonDec
            oAstroSky.moonAlt = moonAlt
            oAstroSky.moonPhase = moonPhase
            oAstroSky.sunAlt = sunAlt
            oAstroSky.sunAZ = sunAZ
            oAstroSky.phaseAngle = phaseAngle
            oAstroSky.rScatter = rScatter
            oAstroSky.mieScatter = mieScatter
            oAstroSky.moonIllum = moonIllum
            oAstroSky.moonBright = moonBright
            oAstroSky.darkBright = darkBright
            oAstroSky.ObsHistory_obsHistID = obsHistID
            self.dbSession.add(oAstroSky)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addAtmosphere(self, rawSeeing, wind, humidity, obsHistID):
        try:
            oAtm = Opsim_Atmosphere()
            oAtm.rawSeeing = rawSeeing
            oAtm.wind = wind
            oAtm.ObsHistory_obsHistID = obsHistID
            self.dbSession.add(oAtm)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addSlewHistory(self, slewCount, startDate, endDate, slewTime, slewDist, obsHistID):
        try:
            oSlewHist = Opsim_SlewHistory()
            oSlewHist.slewCount = slewCount
            oSlewHist.startDate = startDate
            oSlewHist.endDate = endDate
            oSlewHist.slewTime = slewTime
            oSlewHist.slewDist = slewDist
            oSlewHist.ObsHistory_obsHistID = obsHistID
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
            seld.dbSession.add(oSlewAct)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addSlewMaxSpeeds(self, DomAltSpd, DomAzSpd, TelAltSpd, TelAzSpd, RotSpd, slewID):
        try:
            oSlewMaxSpeed = Opsim_SlewMaxSpeeds()
            oSlewMaxSpeed.DomAltSpd = DomAltSpd
            oSlewMaxSpeed.DomAzSpd = DomAzSpd
            oSlewMaxSpeed.TelAltSpd = TelAltSpd
            oSlewMaxSpeed.TelAzSpd = TelAzSpd
            oSlewMaxSpeed.RotSpd = RotSpd
            oSlewMaxSpeed.SlewHistory_slewID = slewID
            self.dbSession.add(oSlewMaxSpeed)
            self.dbSession.commit()
        except:
            self.dbSession.rollback()
            raise

    def addSlewState(self, slewStateDate, tra, tdec, tracking, alt, az, pa, DomAlt,
                     DomAz, TelAlt, TelAz, RotTelPos, Filter, state, slewID):
        try:
            oSlewState = Opsim_SlewState()
            oSlewState.slewStateDate = slewStateDate
            oSlewState.tra = tra
            oSlewState.tdec = tdec
            oSlewState.tracking = tracking
            oSlewState.alt = alt
            oSlewState.az = az
            oSlewState.pa = pa
            oSlewState.DomAlt = DomAlt
            oSlewState.DomAz = DomAz
            oSlewState.TelAlt = TelAlt
            oSlewState.TelAz = TelAz
            oSlewState.RotTelPos = RotTelPos
            oSlewState.Filter = Filter
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
