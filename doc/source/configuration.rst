.. _configuration:

************************************
Working with the Configuration Files
************************************

The cadence for any simulated survey is controlled by setting the values for
parameters contained in the configuration files. These files are located in
Github repository. You will need to clone that repository to where you plan 
on running the simulation, however, the clone does not need to be put in ``$RUN_DIR``.
The configuration file repository is retrieved by::

  git clone https://github.com/lsst-sims/opsim3_config.git

The full path to this clone will be identified in these instructions as ``$OPSIM3_CONFIG_DIR``.
The configuration file clone is checked out into the master branch. This represents the configuration for the current LSST Baseline Cadence and can run a full 10 year simulation. If this is what you want to do, no modifications to the configuration files are necessary. The clone also has other simulation configurations available to it via branches. A full listing of
the branches can be found `here <https://github.com/lsst-sims/opsim3_config/branches/all>`_. Each branch contains a short description of the modifications made compared to the baseline cadence configuration. The clone can be checked out to one of the branches by executing the 
following::

  git checkout -t origin/<name of branch>

where ``<name of branch>`` can found in the listing above.

If you wish to make changes to the configuration, the files are factored into three subdirectories:
``survey``, ``system``, and ``scheduler``. In general, the only files whose
parameters you will change are ``LSST.conf`` and a selected set of proposal
configuration files.

.. toctree::
   :maxdepth: 2

   survey.rst
   system.rst
   scheduler.rst
