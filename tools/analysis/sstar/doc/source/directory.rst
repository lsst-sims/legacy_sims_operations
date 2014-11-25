.. _directory:

*******************
Directory Structure
*******************

We assume that you have been successfully executing ``make`` in the ``sstar`` directory. This section explains the directory structure of the code in the ``sstar`` directory. ::

	+-----------------+--------------------------------------------------------------------+
	| Directory Name  | Description                                                        |
	+=================+====================================================================+
	| bin             | Contains the object files, executables are in the script directory |       
	| images          | Contains default images used in SSTAR                              |
	| output          | Contains output of SSTAR once make_report.sh is executed           |	
	| script          | Contains the executables and python scripts                        |
	| doc             | Sphinx documentation for SSTAR                                     |
	| include         | Contains header files used                                         |
	| src             | Contains source files used                                         |
	+-----------------+--------------------------------------------------------------------+

The ``make_report.sh`` script which is the driver of the SSTAR is in the ``script`` directory.
