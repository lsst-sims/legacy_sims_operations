.. _directory:

*******************
Directory Structure
*******************

The directory structure of ``$SIMS_OPERATIONS_DIR`` is described in this table.

.. code::

	+-----------------+--------------------------------------------------------------------+
	| Directory Name  | Description                                                        |
	+=================+====================================================================+
	| bin             | Contains the main driver script for the OpSim                      |
	| doc             | Contains the Sphinx documentation for the OpSim                    |
	| DataForInstall  | Contains the installation scripts for the OpSim                    |
	| example_conf    | Contains an example set of configuration files (DON'T USE)         |
	| keep            | Contains old stuff we don't want to get rid of                     |
	| log             | Contains the log files generated during the OpSim execution        |
	| python          | Contains all the Python module files for the OpSim                 |
	| site_scons      | Contains Python files related to SCons setup and installation      |
	| templates       | Contains template files used in configuration of the OpSim database|
	| tests           | Contains the unit tests for the OpSim, e.g. DatabaseTest.py, etc.  |
	| tools           | Contains debugging scripts used during the development of OpSim    |
	| ups             | Contains the files related to the EUPS package configuration       |
	+-----------------+--------------------------------------------------------------------+
