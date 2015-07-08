.. _configuration:

************************************
Working with the Configuration Files
************************************

The cadence for any simulated survey is controlled by setting the values for
parameters contained in the configuration files. These files are located in
``$SIMS_OPERATIONS_DIR/conf`` and factored into three subdirectories:
``survey``, ``system``, and ``scheduler``. In general, the only files whose
parameters you will change are ``LSST.conf`` and a selected set of proposal
configuration files.

.. toctree::
   :maxdepth: 2

   survey.rst
   system.rst
   scheduler.rst
