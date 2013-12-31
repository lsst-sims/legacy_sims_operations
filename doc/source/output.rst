.. _simulator_output.rst:

*************************
Working with OpSim Output
*************************

The `DB architecture <architecture.html>`_ section describes the input and output tables of the OpSim. For a more comprehensive set of metrics please take a look at the SSTAR & MAF documentation.

Following are a few sample SQL queries that one could use to query the OpSim output tables.

Sample SQLs
-----------

To get all the observations of an OpSim run identified by sessionID ::

	select * from ObsHistory where Session_sessionID = <sessionID>;
	
To get all the slews of an Opsim run identified by sessionID ::

	select * from SlewHistory where ObsHistory_Session_sessionID = <sessionID>;
	
To get all fields requested by a proposal identified by propID and an Opsim run identified by sessionID ::

	select f.* from Field f join (select Field_fieldID from Proposal_Field where Session_sessionID = <sessionID> and Proposal_propID = <propID>) pf on f.fieldID = pf.Field_fieldID;

Sample Metric
-------------

Following is an example to show how one can create quick plots from the data of OpSim using python, matplotlib & numpy. In this example we shall create histograms for each filter for airmass for the WFD proposals. Attached is the code and output.

.. literalinclude :: _static/airmass.py

Output on stdout is as follows

.. literalinclude :: _static/airmass_output.txt

.. image :: _static/hewelhog_1008_airmass_allfilters.png
   :width: 700 px



