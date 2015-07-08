.. _survey:

Survey
==========

The directory ``$SIMS_OPERATIONS_DIR/conf/survey/`` contains configuration files
which govern the survey programs and master control of the survey. The only
parameters you should change in LSST.conf are the run length and what observing
modes/proposals are going to be used in the simulation.  Below are descriptions 
of common configuration files (LSST.conf is always neeeded), but there are many
variations in the release survey directory and a few subdirectories which have
variants pre-set for specific science goals and simulation investigations.

LSST.conf
---------

LSST.conf is the primary setup file which specifies the observing modes to be
used in this simulation. It also sets parameters such as the length of the run,
the site specific configuation file, and specifies all other configuration file
names and database table names.   In general, the only parameters you should
change in LSST.conf are the run length and what observing modes/proposals are
going to be used in the simulation.  There are short descriptions of the
parameters within the configuration file.  The simulator will generate a log
file describing what it is doing and why. The verbosity parameter sets how
detailed the logging is.  Verbose :math:`\ge 2` will generate HUGE log files
and should only be used for VERY short runs.

Observations will be taken when the cloud value in the cloud table is less than
the parameter maxCloud.  This is the fraction of the sky judged cloudy by the
CTIO night assistant, four times per night, over the 10 year database used for
the simulation.  The cloudiness was recorded as clear eighths of the sky, so
with the default (maxCloud < .7), observations will be taken when
:math:`\frac{5}{8}\rm ths`  or more of the sky is clear.


There are two classes of observing mode - weakLensConf (or WL), and
WLpropConf (or WLTSS). Only observing programs specified in the following way
are included.  WL observing modes only consider how many field/filter
combinations are requested versus how many have been accumulated. WLpropConf
observing modes can have complex cadence requirements in addition to
field/filter observations requirements.  A typical simulation with design area
requirement and design visit requirement and 3.61-type auxiliary proposals uses
the following proposals::

    weakLensConf = ../conf/survey/GalacticPlaneProp.conf
    weakLensConf = ../conf/survey/SouthCelestialPole-18.conf

    WLpropConf = ../conf/survey/Universal-18-0824.conf
    WLpropConf = ../conf/survey/NorthEclipticSpur-18.conf
    WLpropConf = ../conf/survey/DDcosmology1.conf

The following configuration files should be modified with great caution::

    instrumentConf = ../conf/system/Instrument.conf
    schedDownConf = ../conf/system/schedDown.conf
    unschedDownConf = ../conf/system/unschedDown.conf
    filtersConf = ../conf/system/Filters.conf

The configuration files in ``$SIMS_OPERATIONS_DIR/conf/scheduler/`` can be used
to fine tune simulations, but should only be modified with care.  The default
values have been derived over years and hundreds of simulations.

Since the simulator can (and should be) run from a directory tree other than ``$SIMS_OPERATIONS_DIR``, the paths to the configuration files in LSST.conf should be absolute.

.. include:: ../../conf/survey/LSST.conf
   :literal:
   :code: python


Universal-18-0824.conf
----------------------

This proposal is the primary way the WFD observing program has been simulated.
It currently cannot use look ahead.  The ``WLtype = True`` statement makes the
proposal collect field/filter visits in tuples set with ``NumGroupedVisits = n``, where the default is 2 (with the separation set by the
window parameters), but otherwise does not consider cadence.  Advice from early
LSST NEO people was that u and y were not useful for NEOs, so we have been
running those filters without collecting in pairs (note the window parameters).
There are a few important parameters which you may want to play with.
``reuseRankingCount`` determines how often a complete reranking of all
available field/filters is done.  Large values for ``reuseRankingCount`` may
result in sky conditions changing enough that field/filter combinations are
taken which probably shouldn't be.  Small values for ``reuseRankingCount``
slows down the simulation due to the constant reevaluation of the field/filters
ranking.  We have found a value of 10 works well. This means that all possible
ld/filter combinations are ranked based on the internal proposal logic, the
relative importance of each proposal and the slew time to reach them.  The top
10 are chosen; number 1 is observed.  The remaining 9 are reranked and the top
field observed and so on until the 10 are exhausted.

Embedded comments explain most of the parameters well, but a few comments might
be helpful.

- **MaxNumberActiveSequences** is set to a ridiculously high number and is
  irrelevant.

- **RestartLostSequences** is more relevant to WLpropConf proposals without
  ``WLtype = True``.  ``RestartLostSequences`` will restart a sequence which is
  lost due to its missing too many observations.  It is irrelevant for ``WLtype = true`` proposals.

- **RestartCompleteSequences** is relevant to restart a time sequence when too many epoch have been lost and the sequence dies.  It is also relevant for a ``WLtype = true`` proposal where it will restart collection of field/filter pairs after the requested number have been collected.

- **OverflowLevel, ProgressToStartBoost** and **MaxBoostToComplete** are
  parameters which were developed to help deliver the maximum number of fields
  which have the SRD required number of visits in each filter.
  ``OverflowLevel`` sets the amount of field/filter visits allowed beyond the
  number requested.  ``ProgressToStartBoost`` and ``MaxBoostToComplete`` are
  well explained in the embedded comments.  They were inserted to make sure
  that at least some fields collected the requested number of visits in each
  filter.  These are parameters which need to be more fully explored, but will
  likely become irrelevant when look ahead is implemented in WLpropConf proposals.

Selection of the fields to be observed can be done in two ways: 1) define
limits on the sky or 2) explicitly define the fields from the field table to be
used.  Defining limits on the sky is done with the maxReach parameter to control
the declination limits and ``maxAbsRA and minAbsRA`` to control the RA range.  Examples of the RA control can be found in the Rolling subdirectory configuration files. The simulator currently will only observe at defined field centers
chosen to tile the sky with no gaps (kind of hexagonal close packing for the
inscribed hexagon of the circular FOV).  Dithering is currently added in a
postprocessing step.  The ``userRegions`` found in the default configuration
files have been chosen to deliver the appropriate area for each of the
proposals with no gaps.

The conditions which allow observations to be taken are set by airmass limits,
seeing limits and sky brightness limits.  Seeing is calculated from 500nm
zenith seeing values corrected for airmass and wavelength.  Sky brightness is
calculated using the Krisciunus and Schafer algoritm for V band brightness and
corrected to LSST bands.  A single value for z and y sky brightness is used for
twilight observations.  


.. include:: ../../conf/survey/Universal-18-0824.conf
   :literal:
   :code: python


NorthEclipticSpur-18.conf
-------------------------

This proposal collects tuples of observations north of the limits for the WFD
observing area and along the ecliptic north of the WFD area primarily for the
purpose of detecting NEOs.  As such, it does not collect u or y data.  It is a
variant of the Universal proposal.  Note the necessity to allow observations at
higher airmass and larger seeing.

.. include:: ../../conf/survey/NorthEclipticSpur-18.conf
   :literal:
   :code: python


GalacticPlaneProp.conf
----------------------

This proposal collects field/filter combinations with no regard for cadence (proposal type WL), but
could easily be modified to be a WLprop proposal collecting in tuples.

.. include:: ../../conf/survey/GalacticPlaneProp.conf
   :literal:
   :code: python


SouthCelestialPole-18.conf
--------------------------

This proposal collects field/filter combinations with no regard for cadence (proposal type WL), but
could easily be modified to be a WLprop proposal collecting in tuples.


.. include:: ../../conf/survey/SouthCelestialPole-18.conf
   :literal:
   :code: python

DDcosmology1.conf
-----------------

This is a sequence proposal collecting sequences of observations in 5 selected fields for deep
cosmological studies.  There are two sets of sequences since the science wants all 6 filters and
only 5 are mounted at any time.  This proposal needs a bit of modification, since as presented
the parameters mean no main sequence will finish since the missed event parameter is set to zero
and dark time (when u is mounted) is longer than the sequence interval.

.. include:: ../../conf/survey/DDcosmology1.conf
   :literal:
   :code: python
