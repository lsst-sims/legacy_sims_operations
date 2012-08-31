# 
# Weather data table
# 
# F. Pierfederici <fpierfed@noao.edu>
# 
#  Login as 'root' when invoking.

USE LSST;

# If the table is already there, drop it
DROP TABLE IF EXISTS weather;

CREATE TABLE weather (
  w_date  bigint NOT NULL COMMENT 'MJD in seconds',
  w_flux  float NULL      COMMENT 'Average flux',
  w_fwhm  float NOT NULL  COMMENT 'Average FWHM (arcsec)',
  w_fwhmx float NULL      COMMENT 'Average FWHM X (arcsec)',
  w_fwhmy float NULL      COMMENT 'Average FWHM Y (arcsec)',
  secz    float NULL      COMMENT 'Sec(z) (pure number)'
);

CREATE UNIQUE INDEX date_fwhm_idx ON weather (w_date,w_fwhm);
CREATE UNIQUE INDEX date_flux_idx ON weather (w_date,w_flux);

GRANT SELECT, UPDATE, DELETE, INSERT on weather to www;

