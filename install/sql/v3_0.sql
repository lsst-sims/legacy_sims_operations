SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `OpsimDB` ;
CREATE SCHEMA IF NOT EXISTS `OpsimDB` DEFAULT CHARACTER SET utf8 ;
USE `OpsimDB` ;

-- -----------------------------------------------------
-- Table `OpsimDB`.`Session`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Session` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Session` (
  `sessionID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `sessionUser` VARCHAR(80) NOT NULL COMMENT 'operator user name' ,
  `sessionHost` VARCHAR(80) NOT NULL COMMENT 'hostname of processor' ,
  `sessionDate` DATETIME NOT NULL COMMENT 'date of simulation run' ,
  `version` VARCHAR(20) NULL DEFAULT NULL COMMENT 'software version' ,
  `runComment` VARCHAR(200) NULL DEFAULT NULL COMMENT 'user startup comment' ,
  PRIMARY KEY (`sessionID`) ,
  UNIQUE INDEX `s_host_user_date_idx` (`sessionUser` ASC, `sessionHost` ASC, `sessionDate` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Config`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Config` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Config` (
  `configID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `moduleName` VARCHAR(64) NOT NULL COMMENT 'module name' ,
  `paramIndex` INT(11) NOT NULL COMMENT 'index of parameter for module' ,
  `paramName` VARCHAR(64) NOT NULL COMMENT 'parameter name' ,
  `paramValue` VARCHAR(64) NOT NULL COMMENT 'string of parameter value' ,
  `comment` VARCHAR(512) NULL DEFAULT NULL COMMENT 'comment' ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`configID`) ,
  INDEX `fk_config_session_idx` (`Session_sessionID` ASC) ,
  CONSTRAINT `fk_config_session`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Field`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Field` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Field` (
  `fieldID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `fieldFov` FLOAT NOT NULL COMMENT 'Field of View' ,
  `fieldRA` FLOAT NOT NULL COMMENT 'RA in decimal degrees' ,
  `fieldDec` FLOAT NOT NULL COMMENT 'Dec in decimal degrees' ,
  `fieldGL` FLOAT NOT NULL COMMENT 'Galactic L in celestial coord' ,
  `fieldGB` FLOAT NOT NULL COMMENT 'Galactic B in celestial coord' ,
  `fieldEL` FLOAT NOT NULL COMMENT 'approx. Ecliptic L' ,
  `fieldEB` FLOAT NOT NULL COMMENT 'approx. Ecliptic B' ,
  PRIMARY KEY (`fieldID`) ,
  UNIQUE INDEX `field_fov` (`fieldID` ASC, `fieldFov` ASC) ,
  UNIQUE INDEX `fov_gl_gb` (`fieldFov` ASC, `fieldGL` ASC, `fieldGB` ASC) ,
  UNIQUE INDEX `fov_el_eb` (`fieldFov` ASC, `fieldEL` ASC, `fieldEB` ASC) ,
  UNIQUE INDEX `fov_ra_dec` (`fieldFov` ASC, `fieldRA` ASC, `fieldDec` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`ObsHistory`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`ObsHistory` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`ObsHistory` (
  `obsHistID` INT(10) UNSIGNED NOT NULL ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  `filter` VARCHAR(8) NOT NULL COMMENT 'filter name' ,
  `expDate` INT(10) UNSIGNED NOT NULL COMMENT 'sec, date relative to 0s at start' ,
  `expMJD` FLOAT NOT NULL COMMENT 'modified julian date, exposure date' ,
  `night` INT(10) UNSIGNED NOT NULL COMMENT 'count of night being simulated' ,
  `visitTime` FLOAT NOT NULL COMMENT 'sec, exposure duration' ,
  `visitExpTime` FLOAT NOT NULL ,
  `finRank` FLOAT NOT NULL COMMENT 'rank, rank amongst all proposals' ,
  `finSeeing` FLOAT NOT NULL COMMENT 'arcsec, seeing adjusted to filter and airmass' ,
  `transparency` FLOAT NOT NULL COMMENT 'range [0:1], Cloud transparency, 0=photometric, 0<x<1 = spectroscopic, 1 = opaque' ,
  `airmass` FLOAT NOT NULL COMMENT 'none, airmass' ,
  `vSkyBright` FLOAT NOT NULL COMMENT 'mag/arcsec^2, sky brightness adjusted by moon presence' ,
  `filtSkyBright` FLOAT NOT NULL COMMENT 'mag/arcsec^2, sky brightness in current filter' ,
  `rotSkyPos` FLOAT NOT NULL COMMENT 'radians, rotator position on sky' ,
  `lst` FLOAT NOT NULL COMMENT 'radians, local sidereal time' ,
  `alt` FLOAT NOT NULL COMMENT 'radians, field altitude wrt telescope' ,
  `az` FLOAT NOT NULL COMMENT 'radians, field azimuth' ,
  `dist2Moon` FLOAT NOT NULL COMMENT 'radians, distance from field to moon' ,
  `solarElong` FLOAT NOT NULL COMMENT 'DEGREES, solar elongation' ,
  `moonRA` FLOAT NOT NULL ,
  `moonDec` FLOAT NOT NULL ,
  `moonAlt` FLOAT NOT NULL ,
  `moonAZ` FLOAT NOT NULL ,
  `moonPhase` FLOAT NOT NULL ,
  `sunAlt` FLOAT NOT NULL ,
  `sunAZ` FLOAT NOT NULL ,
  `phaseAngle` FLOAT NOT NULL ,
  `rScatter` FLOAT NOT NULL ,
  `mieScatter` FLOAT NOT NULL ,
  `moonIllum` FLOAT NOT NULL ,
  `moonBright` FLOAT NOT NULL ,
  `darkBright` FLOAT NOT NULL ,
  `rawSeeing` FLOAT NOT NULL ,
  `wind` FLOAT NOT NULL ,
  `humidity` FLOAT NOT NULL ,
  `Field_fieldID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`obsHistID`, `Session_sessionID`) ,
  INDEX `oh_field_filter_idx` (`filter` ASC) ,
  INDEX `fk_Obshistory_Session1_idx` (`Session_sessionID` ASC) ,
  INDEX `fk_Obshistory_Field1_idx` (`Field_fieldID` ASC) ,
  CONSTRAINT `fk_Obshistory_Session1`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Obshistory_Field1`
    FOREIGN KEY (`Field_fieldID` )
    REFERENCES `OpsimDB`.`Field` (`fieldID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Proposal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Proposal` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Proposal` (
  `propID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `propConf` VARCHAR(255) NOT NULL COMMENT 'proposal configuration filename name' ,
  `propName` VARCHAR(80) NOT NULL COMMENT 'proposal name' ,
  `objectID` BIGINT(20) NOT NULL COMMENT 'python obj identifier for Proposal instance' ,
  `objectHost` VARCHAR(80) NOT NULL COMMENT 'hostname for proposal object instance' ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`propID`) ,
  INDEX `fk_Proposal_Session1_idx` (`Session_sessionID` ASC) ,
  CONSTRAINT `fk_Proposal_Session1`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`SeqHistory`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`SeqHistory` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`SeqHistory` (
  `sequenceID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `startDate` INT(10) UNSIGNED NOT NULL COMMENT 'simulation sec, sequence start date' ,
  `expDate` INT(10) UNSIGNED NOT NULL COMMENT 'simulation sec, sequence end date' ,
  `seqnNum` INT(10) UNSIGNED NOT NULL COMMENT 'sequence number in the proposal' ,
  `completion` FLOAT NOT NULL COMMENT 'completion status, =1 if success, else 0' ,
  `reqEvents` INT(10) UNSIGNED NOT NULL COMMENT '# requested events' ,
  `actualEvents` INT(10) UNSIGNED NOT NULL COMMENT '# events actually acquired' ,
  `endStatus` INT(10) UNSIGNED NOT NULL COMMENT 'end status: 0=success,1=max missed events, 2=cycle end' ,
  `parent_sequenceID` INT(10) NOT NULL ,
  `Field_fieldID` INT(10) UNSIGNED NOT NULL ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  `Proposal_propID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`sequenceID`) ,
  INDEX `fk_SeqHistory_Field1_idx` (`Field_fieldID` ASC) ,
  INDEX `fk_SeqHistory_Session1_idx` (`Session_sessionID` ASC) ,
  INDEX `fk_SeqHistory_Proposal1_idx` (`Proposal_propID` ASC) ,
  CONSTRAINT `fk_SeqHistory_Field1`
    FOREIGN KEY (`Field_fieldID` )
    REFERENCES `OpsimDB`.`Field` (`fieldID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_SeqHistory_Session1`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_SeqHistory_Proposal1`
    FOREIGN KEY (`Proposal_propID` )
    REFERENCES `OpsimDB`.`Proposal` (`propID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`SlewHistory`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`SlewHistory` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`SlewHistory` (
  `slewID` BIGINT(20) NOT NULL AUTO_INCREMENT ,
  `slewCount` BIGINT(20) NOT NULL COMMENT 'slew count in the run' ,
  `startDate` FLOAT NOT NULL COMMENT 'simulation sec, slew start date' ,
  `endDate` FLOAT NOT NULL COMMENT 'simulation sec, slew end date (shutter open)' ,
  `slewTime` FLOAT NOT NULL COMMENT 'slew total delay in sec' ,
  `slewDist` FLOAT NOT NULL ,
  `ObsHistory_obsHistID` INT(10) UNSIGNED NOT NULL ,
  `ObsHistory_Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`slewID`) ,
  INDEX `fk_SlewHistory_ObsHistory1_idx` (`ObsHistory_obsHistID` ASC, `ObsHistory_Session_sessionID` ASC) ,
  CONSTRAINT `fk_SlewHistory_ObsHistory1`
    FOREIGN KEY (`ObsHistory_obsHistID` , `ObsHistory_Session_sessionID` )
    REFERENCES `OpsimDB`.`ObsHistory` (`obsHistID` , `Session_sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`SlewActivities`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`SlewActivities` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`SlewActivities` (
  `slewActivityID` BIGINT(20) NOT NULL AUTO_INCREMENT ,
  `activity` VARCHAR(16) NOT NULL COMMENT 'slew activity name' ,
  `actDelay` FLOAT NOT NULL COMMENT 'slew activity delay in sec' ,
  `inCriticalPath` VARCHAR(16) NOT NULL COMMENT 'bool, is this activity in the critical path of the total slew delay?' ,
  `SlewHistory_slewID` BIGINT(20) NOT NULL ,
  PRIMARY KEY (`slewActivityID`) ,
  INDEX `fk_SlewActivities_SlewHistory1_idx` (`SlewHistory_slewID` ASC) ,
  CONSTRAINT `fk_SlewActivities_SlewHistory1`
    FOREIGN KEY (`SlewHistory_slewID` )
    REFERENCES `OpsimDB`.`SlewHistory` (`slewID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
MAX_ROWS = 4000000000;


-- -----------------------------------------------------
-- Table `OpsimDB`.`SlewState`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`SlewState` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`SlewState` (
  `slewIniStatID` BIGINT(20) NOT NULL AUTO_INCREMENT ,
  `slewStateDate` FLOAT NOT NULL COMMENT 'simulation sec, observation time for RA DEC coordinates' ,
  `tra` FLOAT NOT NULL COMMENT 'target RA radians' ,
  `tdec` FLOAT NOT NULL COMMENT 'target DEC radians' ,
  `tracking` VARCHAR(16) NOT NULL COMMENT 'bool, tracking state' ,
  `alt` FLOAT NOT NULL COMMENT 'target ALT radians' ,
  `az` FLOAT NOT NULL COMMENT 'target AZ radians' ,
  `pa` FLOAT NOT NULL COMMENT 'target PA radians' ,
  `domAlt` FLOAT NOT NULL COMMENT 'Dome ALT radians' ,
  `domAz` FLOAT NOT NULL COMMENT 'absolute Dome AZ radians' ,
  `telAlt` FLOAT NOT NULL COMMENT 'Telescope ALT radians' ,
  `telAz` FLOAT NOT NULL COMMENT 'absolute Telescope AZ radians' ,
  `rotTelPos` FLOAT NOT NULL COMMENT 'absolute Rotator Angle radians' ,
  `filter` VARCHAR(8) NOT NULL COMMENT 'Filter position' ,
  `state` INT(10) NOT NULL ,
  `SlewHistory_slewID` BIGINT(20) NOT NULL ,
  PRIMARY KEY (`slewIniStatID`) ,
  INDEX `fk_SlewState_SlewHistory1_idx` (`SlewHistory_slewID` ASC) ,
  CONSTRAINT `fk_SlewState_SlewHistory1`
    FOREIGN KEY (`SlewHistory_slewID` )
    REFERENCES `OpsimDB`.`SlewHistory` (`slewID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`SlewMaxSpeeds`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`SlewMaxSpeeds` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`SlewMaxSpeeds` (
  `slewMaxSpeedID` BIGINT(20) NOT NULL AUTO_INCREMENT ,
  `domAltSpd` FLOAT NOT NULL COMMENT 'Dome ALT maximum speed radians/sec' ,
  `domAzSpd` FLOAT NOT NULL COMMENT 'absolute Dome AZ maximum speed radians/sec' ,
  `telAltSpd` FLOAT NOT NULL COMMENT 'Telescope ALT maximum speed radians/sec' ,
  `telAzSpd` FLOAT NOT NULL COMMENT 'absolute Telescope AZ maximum speed radians/sec' ,
  `rotSpd` FLOAT NOT NULL COMMENT 'absolute Rotator Angle maximum speed radians/sec' ,
  `SlewHistory_slewID` BIGINT(20) NOT NULL ,
  PRIMARY KEY (`slewMaxSpeedID`) ,
  INDEX `fk_SlewMaxSpeeds_SlewHistory1_idx` (`SlewHistory_slewID` ASC) ,
  CONSTRAINT `fk_SlewMaxSpeeds_SlewHistory1`
    FOREIGN KEY (`SlewHistory_slewID` )
    REFERENCES `OpsimDB`.`SlewHistory` (`slewID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`TimeHistory`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`TimeHistory` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`TimeHistory` (
  `timeHistID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `date` INT(10) UNSIGNED NOT NULL COMMENT 'simulation sec, event date' ,
  `mjd` FLOAT NOT NULL COMMENT 'MJD, event date' ,
  `night` INT(10) UNSIGNED NOT NULL COMMENT 'count of simulated nights start with 1' ,
  `event` INT(10) UNSIGNED NOT NULL COMMENT '0=startNight,1=moon wane,2=moon wax,3=startYear,4=endDusk,5=startDawn,6=endNight' ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`timeHistID`) ,
  INDEX `th_sessID_event_idx` (`event` ASC) ,
  INDEX `fk_TimeHistory_Session1_idx` (`Session_sessionID` ASC) ,
  CONSTRAINT `fk_TimeHistory_Session1`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`ObsHistory_Proposal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`ObsHistory_Proposal` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`ObsHistory_Proposal` (
  `obsHistory_propID` INT(10) NOT NULL AUTO_INCREMENT ,
  `Proposal_propID` INT(10) UNSIGNED NOT NULL ,
  `propRank` FLOAT NOT NULL ,
  `ObsHistory_obsHistID` INT(10) UNSIGNED NOT NULL ,
  `ObsHistory_Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`obsHistory_propID`) ,
  INDEX `fk_ObsHistory_Proposal_ObsHistory1_idx` (`ObsHistory_obsHistID` ASC, `ObsHistory_Session_sessionID` ASC) ,
  CONSTRAINT `fk_ObsHistory_Proposal_Proposal1`
    FOREIGN KEY (`Proposal_propID` )
    REFERENCES `OpsimDB`.`Proposal` (`propID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ObsHistory_Proposal_ObsHistory1`
    FOREIGN KEY (`ObsHistory_obsHistID` , `ObsHistory_Session_sessionID` )
    REFERENCES `OpsimDB`.`ObsHistory` (`obsHistID` , `Session_sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Cloud`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Cloud` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Cloud` (
  `cloudID` INT NOT NULL AUTO_INCREMENT ,
  `c_date` BIGINT(20) NOT NULL ,
  `cloud` FLOAT NOT NULL ,
  PRIMARY KEY (`cloudID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Seeing`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Seeing` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Seeing` (
  `seeingID` INT NOT NULL AUTO_INCREMENT ,
  `s_date` BIGINT(20) NOT NULL ,
  `seeing` FLOAT NOT NULL ,
  PRIMARY KEY (`seeingID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Log`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Log` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Log` (
  `logID` INT(10) NOT NULL AUTO_INCREMENT ,
  `log_name` VARCHAR(64) NOT NULL ,
  `log_value` VARCHAR(512) NOT NULL ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`logID`) ,
  INDEX `fk_Log_Session1_idx` (`Session_sessionID` ASC) ,
  CONSTRAINT `fk_Log_Session1`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Config_File`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Config_File` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Config_File` (
  `config_fileID` INT NOT NULL AUTO_INCREMENT ,
  `filename` VARCHAR(45) NOT NULL ,
  `data` BLOB NOT NULL ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`config_fileID`) ,
  INDEX `fk_Config_File_Session1_idx` (`Session_sessionID` ASC) ,
  CONSTRAINT `fk_Config_File_Session1`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Proposal_Field`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Proposal_Field` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Proposal_Field` (
  `proposal_field_id` INT(10) NOT NULL AUTO_INCREMENT ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  `Proposal_propID` INT(10) UNSIGNED NOT NULL ,
  `Field_fieldID` INT(10) UNSIGNED NOT NULL ,
  INDEX `fk_Proposal_Field_Session1_idx` (`Session_sessionID` ASC) ,
  INDEX `fk_Proposal_Field_Proposal1_idx` (`Proposal_propID` ASC) ,
  INDEX `fk_Proposal_Field_Field1_idx` (`Field_fieldID` ASC) ,
  PRIMARY KEY (`proposal_field_id`) ,
  CONSTRAINT `fk_Proposal_Field_Session1`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Proposal_Field_Proposal1`
    FOREIGN KEY (`Proposal_propID` )
    REFERENCES `OpsimDB`.`Proposal` (`propID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Proposal_Field_Field1`
    FOREIGN KEY (`Field_fieldID` )
    REFERENCES `OpsimDB`.`Field` (`fieldID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`SeqHistory_ObsHistory`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`SeqHistory_ObsHistory` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`SeqHistory_ObsHistory` (
  `seqhistory_obsHistID` INT(10) NOT NULL AUTO_INCREMENT ,
  `SeqHistory_sequenceID` INT(10) UNSIGNED NOT NULL ,
  `ObsHistory_obsHistID` INT(10) UNSIGNED NOT NULL ,
  `ObsHistory_Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  INDEX `fk_SeqHistory_ObsHistory_SeqHistory1_idx` (`SeqHistory_sequenceID` ASC) ,
  PRIMARY KEY (`seqhistory_obsHistID`) ,
  INDEX `fk_SeqHistory_ObsHistory_ObsHistory1_idx` (`ObsHistory_obsHistID` ASC, `ObsHistory_Session_sessionID` ASC) ,
  CONSTRAINT `fk_SeqHistory_ObsHistory_SeqHistory1`
    FOREIGN KEY (`SeqHistory_sequenceID` )
    REFERENCES `OpsimDB`.`SeqHistory` (`sequenceID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_SeqHistory_ObsHistory_ObsHistory1`
    FOREIGN KEY (`ObsHistory_obsHistID` , `ObsHistory_Session_sessionID` )
    REFERENCES `OpsimDB`.`ObsHistory` (`obsHistID` , `Session_sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`MissedHistory`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`MissedHistory` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`MissedHistory` (
  `missedHistID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  `filter` VARCHAR(8) NOT NULL COMMENT 'filter name' ,
  `expDate` INT(10) UNSIGNED NOT NULL COMMENT 'sec, date relative to 0s at start' ,
  `expMJD` FLOAT NOT NULL COMMENT 'modified julian date, exposure date' ,
  `night` INT(10) UNSIGNED NOT NULL COMMENT 'count of night being simulated' ,
  `lst` FLOAT NOT NULL COMMENT 'radians, local sidereal time' ,
  `Field_fieldID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`missedHistID`, `Session_sessionID`) ,
  INDEX `oh_field_filter_idx` (`filter` ASC) ,
  INDEX `fk_Obshistory_Session1_idx` (`Session_sessionID` ASC) ,
  INDEX `fk_Obshistory_Field1_idx` (`Field_fieldID` ASC) ,
  CONSTRAINT `fk_Obshistory_Session10`
    FOREIGN KEY (`Session_sessionID` )
    REFERENCES `OpsimDB`.`Session` (`sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Obshistory_Field10`
    FOREIGN KEY (`Field_fieldID` )
    REFERENCES `OpsimDB`.`Field` (`fieldID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`SeqHistory_MissedHistory`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`SeqHistory_MissedHistory` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`SeqHistory_MissedHistory` (
  `seqhistory_missedHistID` INT(10) NOT NULL AUTO_INCREMENT ,
  `SeqHistory_sequenceID` INT(10) UNSIGNED NOT NULL ,
  `MissedHistory_missedHistID` INT(10) UNSIGNED NOT NULL ,
  `MissedHistory_Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`seqhistory_missedHistID`) ,
  INDEX `fk_SeqHistory_MissedHistory_SeqHistory1_idx` (`SeqHistory_sequenceID` ASC) ,
  INDEX `fk_SeqHistory_MissedHistory_MissedHistory1_idx` (`MissedHistory_missedHistID` ASC, `MissedHistory_Session_sessionID` ASC) ,
  CONSTRAINT `fk_SeqHistory_MissedHistory_SeqHistory1`
    FOREIGN KEY (`SeqHistory_sequenceID` )
    REFERENCES `OpsimDB`.`SeqHistory` (`sequenceID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_SeqHistory_MissedHistory_MissedHistory1`
    FOREIGN KEY (`MissedHistory_missedHistID` , `MissedHistory_Session_sessionID` )
    REFERENCES `OpsimDB`.`MissedHistory` (`missedHistID` , `Session_sessionID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
