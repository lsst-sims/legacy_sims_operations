.. _running:

*****************
Running the SSTAR
*****************

To run the SSTAR, you must navigate to the script directory of the SSTAR codebase. ``make_report.sh`` is the driver script of the SSTAR. Following is the source of the ``make_report.sh`` script.

To execute the ``make_report.sh`` script.

.. code::

	./make_report.sh <sessionID>

The first section of the ``make_report.sh`` script named 'make_report Config Parameters' allows the user to configure SSTAR.

.. literalinclude:: ../../script/make_report.sh
	:lines: 3-20
	
