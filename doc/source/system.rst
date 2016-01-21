.. _system:

System
==========

The directory ``$OPSIM3_CONFIG_DIR/system`` contains configuration files
which govern the specifications of the telescope, the details for the site,
downtime parameters and details of the granularity of the sky movement, sky
brightness and moon calculations.

DO NOT alter these parameters as many of them are under change control.

Filters.conf
------------

This configuration file is likely to be significantly changed in the future.
It provides default filter usage rules with respect to sky brightness, but
these rules have been moved to each proposal for better control.  It also
defines filter wavelengths and relative exposure time (for all proposals), and
these parameters will eventually be moved to Instrument.conf.  It is possible
you may want to change relative exposure times for a simulation and that is
about all you should change here.

.. include:: ../../example_conf/system/Filters.conf
   :literal:
   :code: python


Instrument.conf
---------------

.. include:: ../../example_conf/system/Instrument.conf
   :literal:
   :code: python


SiteCP.conf
-----------

.. include:: ../../example_conf/system/SiteCP.conf
   :literal:
   :code: python


AstronomicalSky.conf
--------------------

.. include:: ../../example_conf/system/AstronomicalSky.conf
   :literal:
   :code: python


schedDown.conf
--------------

.. include:: ../../example_conf/system/schedDown.conf
   :literal:
   :code: python


unschedDown.conf
----------------
Unscheduled downtime is a single realization of an algorithm which draws random numbers on each day and evaluates whether and how long (integer days) observing stops due to any of four types of events. A minor event, such as a power supply failure, causes a closure for the remainder of the night and next day, and happens 5 out of 365 days. An intermediate event, such as the repair to the filter mechanism, rotator, hexapod or shutter, causes a closure for 3 nights and happens 2 out of 365 days. A major event triggers a closure for 7 nights and occurs 1 out of 730 days. A catastrophic event, such as replacing a raft, triggers a closure for 14 nights and occurs once in 10 years.

.. include:: ../../example_conf/system/unschedDown.conf
   :literal:
   :code: python
