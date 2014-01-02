.. _installation.rst:

*************************
Installing the OpSim Code
*************************
The current source code repository is in a CVS server located internally to the NOAO network. In future releases OpSim will be available through the LSST git repository. Assuming that you have access to the NOAO network and have a CVS account on ``opsimcvs.tuc.noao.edu`` (If you don't have one please contact ``igoodenow@lsst.org``) follow the instructions.

Assumptions
-----------
* You have gcc and g77 installed
* You have python v2.7 installed

Getting the Source
------------------

* Set up the following environment parameters ::

	setenv CVSROOT :ext:<your_cvs_username>@opsimcvs.tuc.noao.edu:/usr/local/cvsroot
	setenv CVS_RSH ssh

* Check out the following repositories in a designated LSST directory. For the purpose of this documentation we shall use ``/lsst`` ::

	cvs co opsim
	cvs co opsim-install

Installation Instructions
-------------------------
  		
* Install the following python packages using your favorite python package installer, here we use easy_install ::

  	easy_install matplotlib
  	easy_install numpy
  	easy_install MySQLdb

* Install the following C/C++ packages using your favorite C/C++ library installer, here we use yum ::

  	yum install mysql5 mysql5-server mysql5-devel mysql5-connector-cpp ElectricFence
  		
* Compile slalib, Navigate to ``/lsst/opsim-install/slalib_c``. For a Mac installation, edit the Makefile and replace "ld -shared" with "gcc -dynamiclib" ::
  		
	make
	make install

* Python setup and install packages from ``/lsst/opsim-install/TableIO`` and ``/lsst/opsim-install/pysla``

* MySQL server should have been installed in the previous ``yum install`` statements. Setup MySQL with an account with username ``www`` and password ``zxcvbnm``. Refer to MySQL documentation for installation, startup scripts, mysqladmin and starting MySQL. Start the MySQL server ::

	mysqladmin -u root password 'some-password'

* Create ``OpsimDB`` database in MySQL and provide the grant priveleges to ``www`` ::
  
	> mysql -u root -p
	create database OpsimDB;
	create user 'www'@'localhost' identified by "zxcvbnm";
	grant all on OpsimDB.* to 'www'@'localhost';
	drop schema OpsimDB;
	source /lsst/opsim/install/sql/v3_0.sql;
	grant all privileges on OpsimDB.* to 'www'@'localhost' identified by 'zxcvbnm' with grant option;
	flush priveleges;
	exit;
	
	> mysql -u www -p
	use OpsimDB;
	source /lsst/opsim-install/Cloud.sql;
	source /lsst/opsim-install/Seeing.sql;
	source /lsst/opsim-install/Field.sql;
		
* To run the OpSim navigate to /lsst/opsim/src ::

	python main.py --startup_comment="Startup comment"

The above instructions should install the Operation Simulator on your machine. If you have issues with the instructions get in touch with ``schandra@noao.edu``
  		

 
  
  
