.. _installation:

*************************
Installing the SSTAR Code
*************************

The current source code repository is in a CVS server located internally to the NOAO network. In future releases OpSim will be available through the LSST git repository. Assuming that you have access to the NOAO network and have a CVS account on ``opsimcvs.tuc.noao.edu`` (If you don't have one, please contact ``igoodenow@lsst.org``) follow the instructions.

Assumptions
-----------
* You have gcc installed. If you don't, please install gcc.
* You have g77 installed. If you don't, please install g77. You need g77 only in the case of Linux based platforms; if you are using OS X you don't need it.
* You have python installed. Version 2.7 or greater is supported.

Getting the Source
------------------

* Set up the following environment parameters ::

	setenv CVSROOT :ext:<your_cvs_username>@opsimcvs.tuc.noao.edu:/usr/local/cvsroot
	setenv CVS_RSH ssh

* Check out the following repositories in a designated LSST directory. For the purpose of this documentation we shall use ``/lsst`` ::

	cvs co sstar
	cvs co opsim-install

Installation Instructions
-------------------------
* Install the following python packages using your favorite python package installer, here we use easy_install ::

	easy_install matplotlib
	easy_install numpy
	easy_install MySQLdb

* Install the following C/C++ packages using your favorite C/C++ library installer, here we use yum ::

	yum install mysql libmysqlclient-dev libargtable2 cpgplot pgplot X11-dev libpng ElectricFence

* Compile slalib, Navigate to ``/lsst/opsim-install/slalib_c``. For a Mac installation, edit the Makefile and replace "ld -shared" with "gcc -dynamiclib" ::

	make
	make install

* Navigate back to ``/lsst/sstar`` and run the following commands ::
	
	make

* To run the SSTAR navigate to ``/lsst/sstar/script`` ::
	
	./make_report <sessionID>

The above instructions should install the SSTAR on your machine. If you have issues with the instructions get in touch with ``schandra@noao.edu``
