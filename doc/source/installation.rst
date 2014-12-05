.. _installation.rst:

*************************
Installing the OpSim Code
*************************
The current source code is in the LSST Simulations sims_operations git (Stash)
repository. However, the code is now available as an EUPS package.

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

  .. code-block:: bash

    eups distrib install -t <tag> sims_operations; setup sims_operations -t <tag>

  Where <tag> is the name of an EUPS package tag.

* Change Database Passwords

  The above step adds a environmental variable $SIMS_OPERATIONS_DIR. Use this to
  navigate to the ``opsim-meta.conf`` file in ``$SIMS_OPERATIONS_DIR/cfg``. In
  the ``[opsim]`` and ``[mysqld]`` sections change the passwords on the ``pass``
  configuration options. Please note the warnings about using special characters
  in the passwords.

* Run the OpSim Configuration

  The OpSim database is installed in a directory separate from the binary files.
  This directory ($OPSIM_RUN_DIR) is by default ``$HOME/opsim-run``, but can be
  changed via the configuration script.

  To setup the OpSim database, run the following command::

    opsim-configure.py --all

  .. warning::

	  The above command will remove any previous configuration setup and database
	  content!

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

The LSST Stack needs to be setup according to the first step in the Installation
Instructions section above. There are a few dependencies that need to be
installed so that the setup commands below won't fail. If theses are not
already installed, here are the required packages::

  eups distrib install mysql -t qserv
  eups distrib install mysqlpython
  eups distrib install twisted -t qserv
  eups distrib install palpy -t sims

Then run::

  setup mysql -t qserv
  setup mysqlpython
  setup twisted -t qserv
  setup palpy -t sims

Once this is done the OpSim code can be setup locally by running the following
commands::

  scons install; setup -k -r .

Finish the setup by following the third and fourth steps in the Installation
Instructions section above.
