.. _system:

System
==========

The directory $SIMS_OPERATIONS_DIR/conf/system/ contains configuration files
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

.. include:: ../../conf/system/Filters.conf
   :literal:
   :code: python


Instrument.conf
---------------

.. include:: ../../conf/system/Instrument.conf
   :literal:
   :code: python


SiteCP.conf
-----------

.. include:: ../../conf/system/SiteCP.conf
   :literal:
   :code: python


AstronomicalSky.conf
--------------------

.. include:: ../../conf/system/AstronomicalSky.conf
   :literal:
   :code: python


schedDown.conf
--------------

.. include:: ../../conf/system/schedDown.conf
   :literal:
   :code: python


unschedDown.conf
----------------

.. include:: ../../conf/system/unschedDown.conf
   :literal:
   :code: python
