import lsst.pex.config as pexConfig

import base
import factories

@pexConfig.registerConfig("Filters30", factories.filtersRegistry,
                          base.FiltersConfig)
class Filters30(base.FiltersConfig):
    """
    This class gathers the information for the standard LSST filters in the
    2x 15 second exposure case.
    """

    def setDefaults(self):
        """
        This function sets the information for the standard filters.
        """
        uFilter = base.FilterConfig()
        uFilter.name = 'u'
        uFilter.minBright = 21.4
        uFilter.maxBright = 30.0
        uFilter.wavelength = 0.34
        uFilter.expFactor = 1.0

        gFilter = base.FilterConfig()
        gFilter.name = 'g'
        gFilter.minBright = 21.0
        gFilter.maxBright = 30.0
        gFilter.wavelength = 0.52
        gFilter.expFactor = 1.0

        rFilter = base.FilterConfig()
        rFilter.name = 'r'
        rFilter.minBright = 20.5
        rFilter.maxBright = 30.0
        rFilter.wavelength = 0.67
        rFilter.expFactor = 1.0

        iFilter = base.FilterConfig()
        iFilter.name = 'i'
        iFilter.minBright = 20.25
        iFilter.maxBright = 30.0
        iFilter.wavelength = 0.79
        iFilter.expFactor = 1.0

        zFilter = base.FilterConfig()
        zFilter.name = 'z'
        zFilter.minBright = 17.5
        zFilter.maxBright = 21.0
        zFilter.wavelength = 0.91
        zFilter.expFactor = 1.0

        yFilter = base.FilterConfig()
        yFilter.name = 'y'
        yFilter.minBright = 17.5
        yFilter.maxBright = 21.0
        yFilter.wavelength = 1.04
        yFilter.expFactor = 1.0

        self.filters = {'u': uFilter, 'g': gFilter, 'r': rFilter, 'i': iFilter,
                        'z': zFilter, 'y': yFilter}
