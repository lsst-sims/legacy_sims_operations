SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

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
  `paramName` VARCHAR(32) NOT NULL COMMENT 'parameter name' ,
  `paramValue` VARCHAR(32) NOT NULL COMMENT 'string of parameter value' ,
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
  `fieldFov` DOUBLE NOT NULL COMMENT 'Field of View' ,
  `fieldRA` DOUBLE NOT NULL COMMENT 'RA in decimal degrees' ,
  `fieldDec` DOUBLE NOT NULL COMMENT 'Dec in decimal degrees' ,
  `fieldGL` DOUBLE NOT NULL COMMENT 'Galactic L in celestial coord' ,
  `fieldGB` DOUBLE NOT NULL COMMENT 'Galactic B in celestial coord' ,
  `fieldEL` DOUBLE NOT NULL COMMENT 'approx. Ecliptic L' ,
  `fieldEB` DOUBLE NOT NULL COMMENT 'approx. Ecliptic B' ,
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
  `obsHistID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `filter` VARCHAR(8) NOT NULL COMMENT 'filter name' ,
  `expDate` INT(10) UNSIGNED NOT NULL COMMENT 'sec, date relative to 0s at start' ,
  `expMJD` DOUBLE NOT NULL COMMENT 'modified julian date, exposure date' ,
  `night` INT(10) UNSIGNED NOT NULL COMMENT 'count of night being simulated' ,
  `visitTime` DOUBLE NOT NULL COMMENT 'sec, exposure duration' ,
  `visitExpTime` DOUBLE NOT NULL ,
  `finRank` DOUBLE NOT NULL COMMENT 'rank, rank amongst all proposals' ,
  `finSeeing` DOUBLE NOT NULL COMMENT 'arcsec, seeing adjusted to filter and airmass' ,
  `transparency` DOUBLE NOT NULL COMMENT 'range [0:1], Cloud transparency, 0=photometric, 0<x<1 = spectroscopic, 1 = opaque' ,
  `airmass` DOUBLE NOT NULL COMMENT 'none, airmass' ,
  `vSkyBright` DOUBLE NOT NULL COMMENT 'mag/arcsec^2, sky brightness adjusted by moon presence' ,
  `filtSkyBright` DOUBLE NOT NULL COMMENT 'mag/arcsec^2, sky brightness in current filter' ,
  `rotSkyPos` DOUBLE NOT NULL COMMENT 'radians, rotator position on sky' ,
  `lst` DOUBLE NOT NULL COMMENT 'radians, local sidereal time' ,
  `alt` DOUBLE NOT NULL COMMENT 'radians, field altitude wrt telescope' ,
  `az` DOUBLE NOT NULL COMMENT 'radians, field azimuth' ,
  `dist2Moon` DOUBLE NOT NULL COMMENT 'radians, distance from field to moon' ,
  `solarElong` DOUBLE NOT NULL COMMENT 'DEGREES, solar elongation' ,
  `obsType` INT(10) NOT NULL ,
  `Session_sessionID` INT(10) UNSIGNED NOT NULL ,
  `Field_fieldID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`obsHistID`) ,
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
  `objectID` BIGINT(20) NULL DEFAULT NULL COMMENT 'python obj identifier for Proposal instance' ,
  `objectHost` VARCHAR(80) NULL DEFAULT NULL COMMENT 'hostname for proposal object instance' ,
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
  `seqnNum` INT(10) UNSIGNED NULL DEFAULT NULL COMMENT 'sequence number in the proposal' ,
  `completion` DOUBLE NOT NULL COMMENT 'completion status, =1 if success, else 0' ,
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
  `startDate` DOUBLE NOT NULL COMMENT 'simulation sec, slew start date' ,
  `endDate` DOUBLE NOT NULL COMMENT 'simulation sec, slew end date (shutter open)' ,
  `slewTime` DOUBLE NOT NULL COMMENT 'slew total delay in sec' ,
  `slewDist` DOUBLE NOT NULL ,
  `ObsHistory_obsHistID` INT(10) UNSIGNED NOT NULL ,
  PRIMARY KEY (`slewID`) ,
  INDEX `fk_SlewHistory_ObsHistory1_idx` (`ObsHistory_obsHistID` ASC) ,
  CONSTRAINT `fk_SlewHistory_ObsHistory1`
    FOREIGN KEY (`ObsHistory_obsHistID` )
    REFERENCES `OpsimDB`.`ObsHistory` (`obsHistID` )
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
  `actDelay` DOUBLE NOT NULL COMMENT 'slew activity delay in sec' ,
  `inCriticalPath` VARCHAR(6) NOT NULL COMMENT 'bool, is this activity in the critical path of the total slew delay?' ,
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
  `slewStateDate` DOUBLE NOT NULL COMMENT 'simulation sec, observation time for RA DEC coordinates' ,
  `tra` DOUBLE NOT NULL COMMENT 'target RA radians' ,
  `tdec` DOUBLE NOT NULL COMMENT 'target DEC radians' ,
  `tracking` VARCHAR(6) NOT NULL COMMENT 'bool, tracking state' ,
  `alt` DOUBLE NOT NULL COMMENT 'target ALT radians' ,
  `az` DOUBLE NOT NULL COMMENT 'target AZ radians' ,
  `pa` DOUBLE NOT NULL COMMENT 'target PA radians' ,
  `DomAlt` DOUBLE NOT NULL COMMENT 'Dome ALT radians' ,
  `DomAz` DOUBLE NOT NULL COMMENT 'absolute Dome AZ radians' ,
  `TelAlt` DOUBLE NOT NULL COMMENT 'Telescope ALT radians' ,
  `TelAz` DOUBLE NOT NULL COMMENT 'absolute Telescope AZ radians' ,
  `RotTelPos` DOUBLE NOT NULL COMMENT 'absolute Rotator Angle radians' ,
  `Filter` VARCHAR(8) NOT NULL COMMENT 'Filter position' ,
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
  `DomAltSpd` DOUBLE NOT NULL COMMENT 'Dome ALT maximum speed radians/sec' ,
  `DomAzSpd` DOUBLE NOT NULL COMMENT 'absolute Dome AZ maximum speed radians/sec' ,
  `TelAltSpd` DOUBLE NOT NULL COMMENT 'Telescope ALT maximum speed radians/sec' ,
  `TelAzSpd` DOUBLE NOT NULL COMMENT 'absolute Telescope AZ maximum speed radians/sec' ,
  `RotSpd` DOUBLE NOT NULL COMMENT 'absolute Rotator Angle maximum speed radians/sec' ,
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
  `MJD` DOUBLE NOT NULL COMMENT 'MJD, event date' ,
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
  `Obshistory_obsHistID` INT(10) UNSIGNED NOT NULL ,
  `propRank` DOUBLE NOT NULL ,
  INDEX `fk_ObsHistory_Proposal_Obshistory1_idx` (`Obshistory_obsHistID` ASC) ,
  PRIMARY KEY (`obsHistory_propID`) ,
  CONSTRAINT `fk_ObsHistory_Proposal_Proposal1`
    FOREIGN KEY (`Proposal_propID` )
    REFERENCES `OpsimDB`.`Proposal` (`propID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ObsHistory_Proposal_Obshistory1`
    FOREIGN KEY (`Obshistory_obsHistID` )
    REFERENCES `OpsimDB`.`ObsHistory` (`obsHistID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Cloud`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Cloud` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Cloud` (
  `cloudID` INT NOT NULL AUTO_INCREMENT ,
  `c_date` BIGINT(20) NULL ,
  `cloud` DOUBLE NULL ,
  PRIMARY KEY (`cloudID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Seeing`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Seeing` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Seeing` (
  `seeingID` INT NOT NULL AUTO_INCREMENT ,
  `s_date` BIGINT(20) NULL ,
  `seeing` DOUBLE NULL ,
  PRIMARY KEY (`seeingID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Log`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Log` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Log` (
  `logID` INT(10) NOT NULL AUTO_INCREMENT ,
  `log_name` VARCHAR(45) NULL ,
  `log_value` VARCHAR(256) NULL ,
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
  `filename` VARCHAR(45) NULL ,
  `data` BLOB NULL ,
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
  INDEX `fk_SeqHistory_ObsHistory_SeqHistory1_idx` (`SeqHistory_sequenceID` ASC) ,
  INDEX `fk_SeqHistory_ObsHistory_ObsHistory1_idx` (`ObsHistory_obsHistID` ASC) ,
  PRIMARY KEY (`seqhistory_obsHistID`) ,
  CONSTRAINT `fk_SeqHistory_ObsHistory_SeqHistory1`
    FOREIGN KEY (`SeqHistory_sequenceID` )
    REFERENCES `OpsimDB`.`SeqHistory` (`sequenceID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_SeqHistory_ObsHistory_ObsHistory1`
    FOREIGN KEY (`ObsHistory_obsHistID` )
    REFERENCES `OpsimDB`.`ObsHistory` (`obsHistID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`Atmosphere`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`Atmosphere` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`Atmosphere` (
  `atmID` INT(10) NOT NULL AUTO_INCREMENT ,
  `rawSeeing` DOUBLE NULL ,
  `wind` DOUBLE NULL ,
  `humidity` DOUBLE NULL ,
  `ObsHistory_obsHistID` INT(10) UNSIGNED NOT NULL ,
  INDEX `fk_Atmosphere_ObsHistory1_idx` (`ObsHistory_obsHistID` ASC) ,
  PRIMARY KEY (`atmID`) ,
  CONSTRAINT `fk_Atmosphere_ObsHistory1`
    FOREIGN KEY (`ObsHistory_obsHistID` )
    REFERENCES `OpsimDB`.`ObsHistory` (`obsHistID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `OpsimDB`.`AstronomicalSky`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `OpsimDB`.`AstronomicalSky` ;

CREATE  TABLE IF NOT EXISTS `OpsimDB`.`AstronomicalSky` (
  `astroID` INT(10) NOT NULL AUTO_INCREMENT ,
  `moonRA` DOUBLE NULL ,
  `moonDec` DOUBLE NULL ,
  `moonAlt` DOUBLE NULL COMMENT '	' ,
  `moonAZ` DOUBLE NULL ,
  `moonPhase` DOUBLE NULL ,
  `sunAlt` DOUBLE NULL ,
  `sunAZ` DOUBLE NULL ,
  `phaseAngle` DOUBLE NULL ,
  `rScatter` DOUBLE NULL ,
  `mieScatter` DOUBLE NULL ,
  `moonIllum` DOUBLE NULL ,
  `moonBright` DOUBLE NULL ,
  `darkBright` DOUBLE NULL ,
  `ObsHistory_obsHistID` INT(10) UNSIGNED NOT NULL ,
  INDEX `fk_AstroSky_ObsHistory1_idx` (`ObsHistory_obsHistID` ASC) ,
  PRIMARY KEY (`astroID`) ,
  CONSTRAINT `fk_AstroSky_ObsHistory1`
    FOREIGN KEY (`ObsHistory_obsHistID` )
    REFERENCES `OpsimDB`.`ObsHistory` (`obsHistID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
