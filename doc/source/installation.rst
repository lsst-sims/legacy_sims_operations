.. _installation.rst:
    

*************************
Installing the OpSim Code
*************************

The current source code is in the LSST sims_operations git (Github)
repository. However, the code is now available via :ref:`install-lsststack`, 
:ref:`install-conda` and :ref:`install-docker`.

.. note:: Since the configuration files are now in a git repository, you will 
          need to have the git command line tool installed on your system.

.. _install-instruct:

Installation Instructions
-------------------------

.. _install-lsststack:

LSST Science Pipelines Install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Install the LSST Science Pipelines

  Installation instructions can be found on the 
  `LSST Science Pipelines <https://pipelines.lsst.io/install/>`_
  pages. Complete the instructions through step 3.
  

* Install the OpSim code

  **NOTE**: If you have or wish to use a system installed MySQL database, do 
  not run the following commands just yet. Please go to the :ref:`system-db` 
  section below. If you do not, then continue on.

  .. code-block:: bash

    eups distrib install -t <tag> sims_operations
    setup sims_operations -t <tag>

  Where <tag> is the name of an EUPS package tag. If you are providing your own
  Python (not using the LSST stack provided one), you will need to declare the
  Python requests package to EUPS by running the following command.

  .. code-block:: bash

    eups declare requests system -r none -m none

  This needs to be done before the setup command is issued. Alternatively, you
  can do the following before running the setup command.

  .. code-block:: bash

    eups distrib install requests

  If you need to override the hostname for the machine, create or change the
  environment variable $OPSIM_HOSTNAME to the appropriate name.

* Change Database Passwords

  The above step adds a environmental variable $SIMS_OPERATIONS_DIR. Use this to
  navigate to the ``opsim-meta.conf`` file in ``$SIMS_OPERATIONS_DIR/cfg``. In
  the ``[opsim]`` and ``[mysqld]`` sections change the passwords on the ``pass``
  configuration options. Please note the warnings about using special characters
  in the passwords.

.. _opsim-config:

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

.. _install-conda:

Conda Installation
~~~~~~~~~~~~~~~~~~

This installation assumes you have installed either the 
`Anaconda Scientific Python Distribution <https://store.continuum.io/cshop/anaconda/>`_
or `Miniconda <http://conda.pydata.org/miniconda.html>`_.

First, add the LSST Conda channel to the configuration::

  conda config --add channels http://eupsforge.net/conda/dev --add channels http://lsst-web.ncsa.illinois.edu/~mareuter/conda/dev

Next, create a Conda environment and activate it::

  conda create -n opsim python
  source activate opsim

Next, install the package::

  conda install lsst-sims-operations

To finish the setup, run::

  source eups-setups.sh
  setup sims_operations

If you need to get out if the environment::

  source deactivate

OpSim requires a database for running, so continue by following the directions 
in the :ref:`OpSim Configuration<opsim-config>` and then the :ref:`running-opsim` sections.

To update the package if a new release is issued::

  conda update lsst-sims-operations

.. _install-docker:

Docker Image
~~~~~~~~~~~~

This installation assumes that you have Docker installed for your particular 
OS of choice. The instructions for getting and using the image are found 
`here <https://hub.docker.com/r/lsst/opsim/>`_.

.. _running-opsim:

Running OpSim
-------------

The above installation sets up the necessary environment for running the OpSim
code, however, the database is not in a running state. It can be easily
started by executing the following command::

	$OPSIM_RUN_DIR/etc/init.d/mysqld start

Once OpSim is installed on a machine you can start a simulation from any 
directory. It is recommended that you create a directory to
run from that is not located with the installed code. You can call this
directory whatever you like, and this documentation will refer to this directory
as ``$RUN_DIR``. For your convenience, make sure to create a ``log`` and
``output`` directory at this location for easy organization of OpSim output.
The configuration for the survey run may be done by reviewing and
customizing values for the parameters defined in the configuration files and 
are described in the :ref:`configuration` section. The configuration files should be 
retrieved from the Github repository and this process will be described in that section. Below is an example command line invocation of OpSim. The ``$OPSIM3_CONFIG_DIR`` is the directory location of the configuration file repository clone.

::

	opsim.py --config=$OPSIM3_CONFIG_DIR/survey/LSST.conf --track=no --startup_comment="Startup comment"

The ``config`` option specifies the location of your modified LSST.conf file. 
The ``track`` option is necessary to avoid adding an entry into the official
run tracking DB. The ``startup_comment`` should contain something descriptive 
about the run you are performing.

If it is ever necessary to shutdown the database, execute the following 
command::

	$OPSIM_RUN_DIR/etc/init.d/mysqld stop

Note that the OpSim code will not connect to the database if it is shutdown.

Getting the Source
------------------

If you require the bleeding edge code, it can be obtained from the LSST
Github repository. Check out the following repositories in a
designated LSST directory. For the purpose of this documentation we shall use
``/lsst`` ::

  git clone https://github.com/lsst/sims_operations.git

If you have write permission to the repository, you will be able to push changes
back to the remote. If you do not have write permission, you can still make
local changes but you will not be able to push them to the remote.

Alternatively, you can setup SSH keys to handle source code control. Please
follow Github's
`procedure <https://help.github.com/articles/generating-ssh-keys>`_. In this
case, the clone URL looks like::

  git clone git@github.com:lsst/sims_operations.git

You should have already installed and configured OpSim by following the
instructions in the :ref:`install-instruct` section. The OpSim code can be setup
locally by running the following commands from the checkout directory::

  eups declare -r . -t $USER sims_operations
  setup sims_operations -t $USER

**NOTE**: You can run the scons ``tests`` and ``doc`` targets without issue. If
you are modifying python code, nothing special needs to be done. If you are
changing the DB setup/configuration files, you needs to run the following
command before running the OpSim configuration step::

  scons install-cfg

.. _system-db:

Using a System Database Installation
------------------------------------

Before installing OpSim from EUPS, the following steps need to be accomplished.
This section assumes that you have already installed the system MariaDB or MySQL
database via your operating system's standard installation methods. The first step 
is to navigate to ``$EUPS_PATH/site`` and create a file called ``manifest.remap``. 
Add the following line to the file::

  mariadb system

The ``mariadb`` is necessary no matter which type of database you use. Its use is due 
to the EUPS dependency. If you are using your own python and not the LSST stack version, 
you need to add the following line to the same file::

  mysqlpython system

Please ensure that your python knows about the MySQLdb python package.

Next, the EUPS setup needs to know about the system packages. This can be
accomplished by running the following command::

  eups declare mariadb system -m none -r none -c

If you are using your own python, also run the following::

  eups declare mysqlpython system -m none -r none -c

After this, you can execute the ``eups distrib install`` and ``setup`` calls
as is from the :ref:`install-instruct` section. Then, continue following the
instructions here.

Since a database install already exists, you just need to create a ``.my.cnf``
file and place it in you home directory. That file looks like::

  [client]
  user     = www
  password = changeit
  # host/port and/or socket
  host     = 127.0.0.1
  port     = 3307
  socket   = /path/to/db/sock/file/mysql.sock

The ``port`` and ``socket`` entries need to be changed to the correct values
for the existing database installation. The ``password`` entry needs to match the
password in the database table setup script described below.

.. warning::

  **DO NOT** run the ``opsim-configure.py`` command above as is it unnecessary.

To finish the setup you need to create the OpsimDB and populate some tables.
Copy the ``setup_db.sh`` script from the ``$SIMS_OPERATIONS_DIR/tools``
directory and edit the password variable at the top. Then execute the
following::

  sh setup_db.sh

This should create the OpsimDB and populate some initial tables. You should
now be able to run OpSim by following the :ref:`running-opsim` section above.
However, you can ignore the ``mysql`` start and stop commands as the existing
installation will probably already be running. If it is not, please refer to 
your operating system's documentation for handling the MySQL daemon.
