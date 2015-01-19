.. _installation.rst:

*************************
Installing the OpSim Code
*************************
The current source code is in the LSST Simulations sims_operations git (Stash)
repository. However, the code is now available as an EUPS package.

.. _install-instruct:

Installation Instructions
-------------------------

* Install the LSST Stack Setup

  .. code-block:: bash

    NEWINSTALL_URL=https://sw.lsstcorp.org/eupspkg/newinstall.sh
    export EUPS_PKGROOT=${NEWINSTALL_URL}
    INSTALL_DIR=root/directory/where/sims_operations/stack/will/be/installed
    # e.g. ~/lsst Please note that $INSTALL_DIR must be empty
    cd $INSTALL_DIR
    curl -O ${NEWINSTALL_URL}
    # script below will ask some questions. Unless you know what you're doing,
    # and you need a fine tuned setup, please answer 'yes' everywhere.
    bash newinstall.sh
    . loadLSST.bash

* Install the OpSim code

  **NOTE**: If you have an existing database installation (i.e. a system
  installed mysql) and wish to use that, do not run the following commands
  just yet. Please go to the :ref:`existing-db` section below. If you do not,
  then continue on.

  .. code-block:: bash

    eups distrib install -t <tag> sims_operations
    setup sims_operations -t <tag>

  Where <tag> is the name of an EUPS package tag. If you need to override the
  hostname for the machine, create or change the environment variable
  $OPSIM_HOSTNAME to the appropriate name.

* Change Database Passwords

  The above step adds a environmental variable $SIMS_OPERATIONS_DIR. Use this to
  navigate to the ``opsim-meta.conf`` file in ``$SIMS_OPERATIONS_DIR/cfg``. In
  the ``[opsim]`` and ``[mysqld]`` sections change the passwords on the ``pass``
  configuration options. Please note the warnings about using special characters
  in the passwords.

* Run the OpSim Configuration

  The OpSim database is installed in a directory separate from the binary files.
  This directory is by default ``$HOME/opsim-run``, but can be changed via
  passing the -R flag and a directory path to the configuration script. The
  documentation below will refer to this directory location as $OPSIM_RUN_DIR,
  but please note that this is not an environmental variable. The configuration
  script does not create one.

  To setup the OpSim database, run the following command::

    opsim-configure.py --all

  .. warning::

	  The above command will remove any previous configuration setup and database
	  content!

.. _running-opsim:

Running OpSim
-------------

The above installation sets up the necessary environment for running the OpSim
code. However, the database is not in a running state, but this can be easily
started by executing the following command::

	$OPSIM_RUN_DIR/etc/init.d/mysqld start

The OpSim code can be run as follows::

	opsim.py --startup_comment="Startup comment"

To shutdown the database, execute the following command::

	$OPSIM_RUN_DIR/etc/init.d/mysqld stop

However, the OpSim code will not connect to the database if it is shutdown, so
only do this if necessary.

Getting the Source
------------------

If one requires using the bleeding edge code, it can be obtained from the LSST
Simulations Stash repository. Check out the following repositories in a
designated LSST directory. For the purpose of this documentation we shall use
``/lsst`` ::

  git clone https://<your_stash_username>@stash.lsstcorp.org/scm/sim/sims_operations.git

If you need to only obtain a readonly copy, omit the ``<your_stash_username>@``
from the clone command.

You should have already installed and configured OpSim by following the
instructions in the :ref:`install-instruct` section. The OpSim code can be setup
locally by running the following command from the checkout directory::

  setup sims_operations -t $USER

**NOTE**: You can run the scons ``tests`` and ``doc`` targets without issue. If
you are modifying python code, nothing special needs to be done. If you are
changing the DB setup/configuration files, one needs to run the following
command before running the OpSim configuration step::

  scons install-cfg

.. _existing-db:

Using an Existing Database Installation
---------------------------------------

Before installing OpSim from EUPS, the following steps need to be accomplished.
First, navigate to ``$EUPS_PATH/site`` and create a file called
``manifest.remap``. Add the following line to the file::

  mysql system

If you are using your own python and not the LSST stack version, you need to
add the following line to the same file::

  mysqlpython system

Please ensure that your python knows about the MySQLdb python package.

Next, the EUPS setup needs to know about the system packages. This can be
accomplished by running the following command::

  eups declare mysql system -m none -r none -c

If you are using your own python, also run the following::

  eups declare mysqlpython system -m none -r none -c

After this, one can execute the ``eups distrib install`` and ``setup`` calls
as is from the :ref:`install-instruct` section. Then, continue following the
instructions here.

Since a database install already exists, one just needs to create a ``.my.cnf``
file and place it in you home directory. That file looks like::

  [client]
  user     = www
  pass     = changeit
  # host/port and/or socket
  host     = 127.0.0.1
  port     = 3307
  socket   = /path/to/db/sock/file/mysql.sock

The ``port`` and ``socket`` entries need to be changed to the correct values
for the existing database installation. The ``pass`` entry needs to match the
password in the database table setup script described below.

.. warning::

  **DO NOT** run the ``opsim-configure.py`` command above as is it unnecessary.

To finish the setup, one needs to create the OpsimDB and populate some tables.
Navigate to the ``$SIMS_OPERATIONS_DIR/tools`` directory and edit the password
variable at the top of the ``setup_db.sh`` script. Then execute the following::

  sh setup_db.sh

This should create the OpsimDB and populate some initial tables. One should
now be able to run OpSim by following the :ref:`running-opsim` section above.
However, one can ignore the ``mysql`` start and stop commands as the existing
installation will probably already be running.
