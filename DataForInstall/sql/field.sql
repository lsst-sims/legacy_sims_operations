# 
# Field related tables
# 
#  Login as 'root' when invoking.

USE LSST;

# If some of the tables we want to create are already there, drop them
DROP TABLE IF EXISTS Field;

# Field
CREATE TABLE Field (
    fieldID     int unsigned AUTO_INCREMENT,
    fieldFov    float NOT NULL COMMENT 'Field of View',
    fieldRA     float NOT NULL COMMENT 'RA in decimal degrees',
    fieldDec    float NOT NULL COMMENT 'Dec in decimal degrees',
    fieldGL     float NOT NULL COMMENT 'Galactic L in celestial coord',
    fieldGB     float NOT NULL COMMENT 'Galactic B in celestial coord',
    fieldEL     float NOT NULL COMMENT 'approx. Ecliptic L',
    fieldEB     float NOT NULL COMMENT 'approx. Ecliptic B',
    PRIMARY KEY (fieldID)
);
create unique index field_fov on Field (fieldID,fieldFov);
create unique index fov_gl_gb on Field (fieldFov,fieldGL,fieldGB);
create unique index fov_el_eb on Field (fieldFov,fieldEL,fieldEB);
create unique index fov_ra_dec on Field (fieldFov,fieldRA,fieldDec);

# Grant privileges to the www user
GRANT SELECT, UPDATE, DELETE, INSERT on Field to www;

