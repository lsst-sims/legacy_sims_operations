#!/bin/bash

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

# To push documenation, one needs to make sure that the clone is up-to-date
# Then run this script: ./publish.sh

# To push documentation for a version (a git tag), one needs to make sure
# that the clone is checked out to the tag. Then run this script passing it
# any integer: ./publish.sh 0

DIR=$(cd "$(dirname "${0}")"; pwd -P)
cd ${DIR}/..
(
echo "Generating documentation"
scons doc
)
DOC_ROOT_PATH=/home/lsst/docs
if [ -z ${1} ]; then
  VERSION="master"
else
  VERSION=$(python -c "import lsst.sims.operations.version as version; print version.__version__")
  # Version X.Y.Z will be truncated to X.Y
  VERSION=${VERSION%.*}
fi
echo "Copying documentation from ${PWD} to ${DOC_ROOT_PATH}/${VERSION}"
if [ ! -d "${DOC_ROOT_PATH}/${VERSION}" ]; then
  mkdir -p ${DOC_ROOT_PATH}/${VERSION}
fi
cp -r doc/build/html/* ${DOC_ROOT_PATH}/${VERSION}
