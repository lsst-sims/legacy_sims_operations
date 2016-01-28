.. _scheduler:

Scheduler
==========

The directory ``$OPSIM3_CONFIG_DIR/scheduler`` contains the configuration
files which govern look-ahead calculations and details of how ranked
observations are chosen, as well as  what filters are available and when, and
by how much to avoid various astronomical objects, such as the Moon.


Scheduler.conf
--------------

.. include:: ../../example_conf/scheduler/Scheduler.conf
   :literal:
   :code: python


SchedulingData.conf
-------------------

.. include:: ../../example_conf/scheduler/SchedulingData.conf
   :literal:
   :code: python
