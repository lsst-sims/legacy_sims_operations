import os

import SCons.Util

import utils

class Find(object):
    def __init__(self):
        self.log = utils.Log()

    def _getBinPath(self, binName, msg=None):
        if msg is None:
            msg = "Looking for %s" % binName
        self.log.info(msg)
        binFullPath = SCons.Util.WhereIs(binName)
        if not binFullPath:
            raise SCons.Errors.StopError('Could not locate binary : %s' %
                                         binName)
        else:
            return binFullPath

    def _findPrefixFromPath(self, key, binFullPath):
        if not binFullPath:
            self.log.fail("_findPrefixFromPath : empty path specified "
                          "for key %s" % key)
        (binpath, binname) = os.path.split(binFullPath)
        (basepath, bin) = os.path.split(binpath)
        if bin.lower() == "bin":
            prefix = basepath

        if not prefix:
            self.log.fail("Could not locate install prefix for product "
                          "containing next binary : " % binFullPath)
        return prefix

    def prefixFromBin(self, key, binName):
        """
        returns install prefix for  a dependency named 'product'
        - if the dependency binary is PREFIX/bin/binName then PREFIX is used
        """
        prefix = self._findPrefixFromPath(key, self._getBinPath(binName))
        return prefix
