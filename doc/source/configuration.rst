.. _configuration:

**************************************
Working with the Configuration Files
**************************************

Any simulated survey is controlled by setting the values for parameters contained in the configuration files.
These files are located in /lsst/opsim/conf and factored into three subdirectories: survey, system, and scheduler. In general, the only files whos parameters you will change are LSST.conf and a selected set of proposal/observing mode files.

.. toctree::
   :maxdepth: 2

   survey.rst
   system.rst
   scheduler.rst
