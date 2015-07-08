.. _simulator_output.rst:

*************************
Working with OpSim Output
*************************

The :ref:`architecture.rst` section describes the input 
and output tables of the OpSim database. 
There are several ways to analyze the information in the output tables in
order to understand how the configuration file parameters 
have impacted the survey performance.

It is recommended that you use the tool ``modifySchema.sh`` to create an extra 
output table in the MySQL database called ``summary_<hostname>_<sessionID>``.
Each simulation is uniquely identified by the name of the machine where it was created 
``<hostname>`` and an automatically incremented identifier ``<sessionID>``.
This table contains
the most commonly used fields from the output tables, and calculates and adds
useful quantities such as ``fiveSigmaDepth`` and a set of dithered coordinates.
Here is a description of the `Summary table columns <https://confluence.lsstcorp.org/display/SIM/Summary+Table+Column+Descriptions>`_.  
Additionally this script exports this table and  all the information from a 
single ``sessionID`` to a MySQL (.sql) file and an SQLite (_sqlite.db) file.
To run the script from the local directory from where you are running the
simulator, simply execute ``$SIMS_OPERATIONS_DIR/tools/modifySchema.sh <sessionID>``.


Metrics Analysis Framework
==========================
The most comprehensive set of tools available is the
`Metrics Analysis Framework (MAF) <https://confluence.lsstcorp.org/display/SIM/MAF+documentation>`_.  
This framework provides tools for reading and interacting with the database,
as well as many predefined analysis scripts that will help you gain insight 
into a simulated survey. You can build on this tool by writing your 
own customized analyses. Because MAF primarily uses the Summary table from
the SQLite export file, you MUST run the ``modifySchema.sh`` script before 
using MAF.

Queries using mySQL
===================
The most direct method is to simply query the OpSim database using mySQL.
Here are some examples:

To get all the observations of an OpSim run identified by sessionID ::

	select * from ObsHistory where Session_sessionID = <sessionID>;

To get all the slews of an OpSim run identified by sessionID ::

	select * from SlewHistory where ObsHistory_Session_sessionID = <sessionID>;

To get all fields requested by a proposal identified by propID and an OpSim run identified by sessionID ::

	select f.* from Field f join (select Field_fieldID from Proposal_Field where Session_sessionID = <sessionID> and Proposal_propID = <propID>) pf on f.fieldID = pf.Field_fieldID;

Write your own Script
=====================
Without too much effort you can create quick plots from the database
using python, matplotlib and numpy. 

In this example of a python script, we read the database, extract the 
required information and plot the results. The output is  histograms 
of the airmass for each filter for visits requested by the WFD proposals. 

.. literalinclude :: _static/airmass.py

Results of the script are written to the standard output (stdout).

.. literalinclude :: _static/airmass_output.txt

A figure (png format) showing the results is generated.

.. image :: _static/hewelhog_1008_airmass_allfilters.png
   :width: 700 px
