#!/bin/sh

# LSST Data Management System
# Copyright 2015 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.


# Upload sphinx documentation for operations simulator to web-server.
# Special thanks to Fabrice Jammes, IN2P3 for the original script.

# To push documentation for a version (a git tag), one needs to make sure
# that the clone is checked out to the tag. Then run this script passing it
# any integer: publish.sh 0

# eval `ssh-agent -s`
# ssh-add ~/.ssh/id_rsa_lsst
DIR=$(cd "$(dirname "$0")"; pwd -P)
cd $DIR/..
(
echo "Generating documentation"
scons doc
)
REMOTE_HOST=opsimcvs.tuc.noao.edu
DOC_ROOT_PATH=/var/www/html/docs/simulator
if [ -z $1 ]; then
  VERSION=""
else
  VERSION=$(python -c "import lsst.sims.operations.version as version; print version.__version__")
fi
echo "Uploading documentation from $PWD to $REMOTE_HOST"
scp -r doc/build/html/* ${REMOTE_HOST}:${DOC_ROOT_PATH}/${VERSION}
