.. _simulator_output.rst:

*************************
Working with OpSim Output
*************************

The :ref:`architecture.rst` section describes the input and output tables of the OpSim database. 
There are several ways to analyze the information in the output tables in order to understand 
how the configuration file parameters have affected the survey performance.

It is recommended that you use the tool ``modifySchema.sh`` which extracts all the information
pertaining to a particular ``<sessionID>`` to a single file but in three different formats: 
ASCII (.dat), MySQL (.sql), and SQLite (_sqlite.db). 
Importantly, this script generates an extra table which contains the most 
commonly used fields from the output tables, and calculates and adds additional useful 
quantities such as ``fiveSigmaDepth`` and a set of dithered coordinates.
In the MySQL database which OpSim writes to, and in the exported .sql file, this new table is 
called ``summary_<hostname>_<sessionID>``. In the exported _sqlite.db file it is called 
``Summary``. 
Here is a description of the columns in this `table <https://confluence.lsstcorp.org/display/SIM/Summary+Table+Column+Descriptions>`_.  
To run the script from the local directory from where you are running the
simulator, simply execute ``$SIMS_OPERATIONS_DIR/tools/modifySchema.sh <sessionID>``.
If a directory named ``output`` exists in the directory where you call this script, the 
files will be written here instead of the current directory.


Metrics Analysis Framework
==========================
The most comprehensive set of analysis tools available is the
`Metrics Analysis Framework (MAF) <https://confluence.lsstcorp.org/display/SIM/MAF+documentation>`_ 
which is available as an EUPS package.  This framework provides tools for reading and interacting 
with the database, as well as many predefined analysis scripts that will help you gain insight 
into a simulated survey. You can build on this tool by writing your own customized analyses. 
Because MAF primarily uses the ``Summary`` table from the SQLite export file, you MUST run the
``modifySchema.sh`` script before using MAF.

Queries using mySQL
===================
The most direct method of examining a simulated survey is to simply query the OpSim database using 
mySQL.  Here are some examples:

To get all the observations of an OpSim run identified by sessionID ::

	select * from ObsHistory where Session_sessionID = <sessionID>;

To get all the slews of an OpSim run identified by sessionID ::

	select * from SlewHistory where ObsHistory_Session_sessionID = <sessionID>;

To get all fields requested by a proposal identified by propID and an OpSim run identified by sessionID ::

	select f.* from Field f join (select Field_fieldID from Proposal_Field where Session_sessionID = <sessionID> and Proposal_propID = <propID>) pf on f.fieldID = pf.Field_fieldID;

Write your own Script
=====================
You can also create plots from the database using Python, matplotlib and numpy. 

In this example of a Python script, we read the database, extract the 
required information and plot the results. The output is histograms 
of the airmass for each filter for visits requested by the WFD (Wide-Fast-Deep) proposals. 

.. literalinclude :: _static/airmass.py

Results of the script are written to the standard output (stdout).

.. literalinclude :: _static/airmass_output.txt

A figure (png format) showing the results is generated.

.. image :: _static/hewelhog_1008_airmass_allfilters.png
   :width: 700 px
