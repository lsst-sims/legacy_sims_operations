# 
# Observation History  related tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS ObsHistory;


# ObsHistory
CREATE TABLE ObsHistory (
    obsHistID  int unsigned AUTO_INCREMENT PRIMARY KEY,
    sessionID  int unsigned NOT NULL COMMENT 'session identifier',
    propID     int unsigned NOT NULL COMMENT 'proposal identifier',
    fieldID    int unsigned NOT NULL COMMENT 'field identifier',
    filter     varchar(8)   NOT NULL COMMENT 'filter name',
    seqnNum    int unsigned          COMMENT 'sequence number in the proposal',
    subseq     varchar(8)   NOT NULL COMMENT 'subsequence name',
    pairNum    int unsigned          COMMENT 'pair number in the subsequence',
    expDate    int unsigned NOT NULL COMMENT 'sec, date relative to 0s at start',
    expMJD     double NOT NULL COMMENT 'modified julian date, exposure date',
    night      int unsigned NULL COMMENT 'count of night being simulated',
    expTime    float NOT NULL COMMENT 'sec, exposure duration',
    slewTime   float NOT NULL COMMENT 'sec, slew duration',
    slewDist   float NOT NULL COMMENT 'unused, slew distance',
    rotSkyPos  float NOT NULL COMMENT 'radians, rotator position on sky',
    rotTelPos  float NOT NULL COMMENT 'radians, rotator position on telescope',
    fldVisits  int unsigned NOT NULL COMMENT 'count, field visits to expDate',
    fldInt     int unsigned NOT NULL COMMENT 'count, interval since last field visit',
    fldFltrInt int unsigned NOT NULL COMMENT 'count, interval since last field/filter visit',
    propRank   float NOT NULL COMMENT 'rank, rank within proposal',
    finRank    float NOT NULL COMMENT 'rank, rank amongst all proposals',
    maxSeeing  float NOT NULL COMMENT 'arcsec, maximum acceptable seeing',
    rawSeeing  float NOT NULL COMMENT 'arcsec, raw seeing from Climate Model',
    seeing     float NOT NULL COMMENT 'arcsec, seeing adjusted to filter and airmass',
    xparency   float NOT NULL COMMENT 'range [0:1], Cloud transparency, 0=photometric, 0<x<1 = spectroscopic, 1 = opaque',
    cldSeeing  float NOT NULL COMMENT 'unused, seeing adjusted by transparency',
    airmass    float NOT NULL COMMENT 'none, airmass',
    VskyBright float NOT NULL COMMENT 'mag/arcsec^2, sky brightness adjusted by moon presence',
    filtSky    float NOT NULL COMMENT 'mag/arcsec^2, sky brightness in current filter',
    fieldRA    float NOT NULL COMMENT 'radians, field right ascension',
    fieldDec   float NOT NULL COMMENT 'radians, field declination',
    lst        float NOT NULL COMMENT 'radians, local sidereal time',
    altitude   float NOT NULL COMMENT 'radians, field altitude wrt telescope',
    azimuth    float NOT NULL COMMENT 'radians, field azimuth',
    dist2Moon  float NOT NULL COMMENT 'radians, distance from field to moon',
    moonRA     float NOT NULL COMMENT 'radians, moon right ascension',
    moonDec    float NOT NULL COMMENT 'radians, moon declination',
    moonAlt    float NOT NULL COMMENT 'radians, moon altitude wrt telescope',
    moonPhase  float NOT NULL COMMENT '% in range [0-100], phase of moon',
    sunAlt     float NOT NULL COMMENT 'radians, sun altitude',
    sunAz      float NOT NULL COMMENT 'radians, sun azimuth',
    phaseAngle float NOT NULL COMMENT 'degrees, moon phase angle',
    rScatter   double NOT NULL COMMENT 'Rayleigh scatter from moonlight',
    mieScatter float NOT NULL COMMENT 'Mie scatter from moonlight',
    moonIllum  float NOT NULL COMMENT 'Moon illuminance out of atmosphere',
    moonBright float NOT NULL COMMENT 'nanoLamberts, Moon brightness in atmosphere with scatter',    
    darkBright float NOT NULL COMMENT 'nanoLamberts, Dark sky brightness',
    solarElong float NULL COMMENT 'DEGREES, solar elongation'
        );
CREATE INDEX oh_sessID_idx ON ObsHistory (sessionID);
CREATE INDEX oh_propID_idx ON ObsHistory (sessionID,propID);
CREATE INDEX oh_field_filter_idx ON ObsHistory (sessionID, fieldID, filter);
CREATE INDEX oh_seq_subseq_idx ON ObsHistory (sessionID, seqnNum, subseq);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on ObsHistory to www;

