.. _output:

******
Output
******

As part of the SSTAR the execution creates a materialized output table named ``output_<machine>_<sessionID>``. This is the table from which all the statistics are created. The SSTAR copies the ``ObsHistory`` (Observation History) table and then adds other post processed columns into the "output" table. This table along with the SSTAR Standard report is available for release to the scientists for further analysis. Following are the columns in the "output" table. ::

	+------------------------+------------------+--------------+----------------------------------------------------------------------+
	| Field                  | Type             | Units        | Description                                                          |
	+========================+==================+==============+======================================================================+
	| obsHistID              | int(10) unsigned | none         | Unique visit identifier                                              |
	| sessionID              | int(10) unsigned | none         | Session identifier (run of simulator)                                |
	| propID                 | int(10)          | none         | Proposal identifier (different for every run)                        |
	| fieldID                | int(10) unsigned | none         | Field identifier (unique for each RA/Dec)                            |
	| fieldRA                | float            | radians      | Field Right Ascension                                                |
	| fieldDec               | float            | radians      | Field Declination                                                    |
	| filter                 | varchar(8)       | char         | Filter used at this visit (ugrizy)                                   |
	| expDate                | int(10) unsigned | sec          | Time relative to 0 sec at start of OpSim run                         |
	| expMJD                 | decimal(11,6)    | MJD          | Date & Time of visit (MJD of visit)                                  |
	| night                  | int(10) unsigned | count        | Night number                                                         |
	| visitTime              | float            | sec          | Visit duration (includes shutter and readout time)                   |
	| visitExpTime           | float            | sec          | Visit Exposure Time                                                  |
	| finRank                | float            | rank         | Target rank among all proposals                                      |
	| finSeeing              | float            | arcsec       | Seeing adjusted to filter and airmass                                |
	| transparency           | float            | [0:1]        | Cloud transparency (0=photometric, 0−1=spectroscopic, 1=opaque)      |
	| airmass                | float            | none         | Airmass                                                              |
	| vSkyBright             | float            | mag/arcsec^2 | Sky brightness adjusted by moon presence (in the V filter)           |
	| filtSkyBright          | float            | mag/arcsec^2 | Sky brightness in V filter adjusted to current filter                |
	| rotSkyPos              | float            |              | Rotator Sky Position                                                 |
	| lst                    | float            | radians      | Local Sidereal Time                                                  |
	| altitude               | float            | radians      | Field altitude with respect to telescope                             |
	| azimuth                | float            | radians      | Field azimuth with respect to telescope                              |
	| dist2Moon              | float            | radians      | Distance from field to the Moon                                      |
	| solarElong             | float            |              | Solar Elongation                                                     |
	| moonRA                 | float            | radians      | Moon Right Ascension                                                 |
	| moonDec                | float            | radians      | Moon Declination                                                     |
	| moonAlt                | float            | radians      | Moon Altitude with respect to the Telescope                          |
	| moonAZ                 | float            | radians      | Moon Azimuth                                                         |
	| moonPhase              | float            | [0:100]      | Percent illumination of the Moon (0=new, 100=full)                   |
	| sunAlt                 | float            | radians      | Sun Altitude                                                         |
	| sunAz                  | float            | radians      | Sun Azimuth                                                          |
	| phaseAngle             | float            |              | Parameter used in V sky brightness transformation                    |
	| rScatter               | float            |              | Parameter used in V sky brightness transformation                    |
	| mieScatter             | float            |              | Parameter used in V sky brightness transformation                    |
	| moonIllum              | float            |              | Parameter used in V sky brightness transformation                    |
	| moonBright             | float            |              | Parameter used in V sky brightness transformation                    |
	| darkBright             | float            |              | Parameter used in V sky brightness transformation                    |
	| rawSeeing              | float            |              | Raw Seeing                                                           |
	| wind                   | float            |              | Wind                                                                 |
	| humidity               | float            |              | Humidity                                                             |
	| slewDist               | float            | radians      | Slew Distance                                                        |
	| slewTime               | float            | sec          | Slew Time                                                            |
	| fivesigma              | float            | mag/arcsec^2 | 5 Sigma Limiting Magnitude                                           |
	| perry_skybrightness    | float            | mag/arcsec^2 | Sky Brightness based on Perry's ETC method                           |
	| fivesigma_ps           | float            | mag/arcsec^2 | 5 Sigma Limiting Magnitude based on Perry's ETC method               |
	| skybrightness_modified | float            |              | Sky Brightness Modified                                              |
	| fivesigma_modified     | float            |              | 5 Sigma Limiting Magnitude based on Sky Brightness Modified          |
	| hexdithra              | double           | radians      | Dithered Right Ascension                                             |
	| hexdithdec             | double           | radians      | Dithered Declination                                                 |
	| vertex                 | int(11)          |              | Vertex                                                               |
	+------------------------+------------------+--------------+----------------------------------------------------------------------+
	
A sample SSTAR standard report is attached :download:`here <_static/sstar.pdf>`.
