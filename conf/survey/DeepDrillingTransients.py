import lsst.pex.config as pexConfig
from baseConf import BaseConfig
# Configuration for each filter-subsequence
#MasterSubSequence = main

#   SubSeqName	     = name of subsequence
#                      Default = value defined for SubSeqFilters
#   SubSeqFilters    = ordered list of filters.   No default.
#   SubSeqExposures  = filter-ordered list of exposure counts 
#                      Default = 1 for missing values
#   SubSeqEvents     = Requested Number Events per Completed Sequence. 
#                      No default.
#   SubSeqMaxMissed  = Maximum number of events the proposal allowed to miss
#                      in a sequence without declaring it as lost.   No default.
#   SubSeqInterval   = Time interval (sec) between events in a Sequence.
#                      No default.
#   SubSeqWindowStart= Time at which event's priority starts rising. No default
#   SubSeqWindowMax  = Time at which event's priority reaches max.  No default.
#   SubSeqWindowEnd  = Time at which event is abandoned. No default.

class BaseSequenceConfig(pexConfig.Config):
    name = pexConfig.Field('Name of sequence', str)
    numSequenceEvents = pexConfig.Field('Number of requested events for this sequence', int)
    numMaxMissed = pexConfig.Field('Number of missed events allowed for this sequence', int)
    sequenceInterval = pexConfig.Field('Valid interval in seconds', int)
    sequenceWindowStart = pexConfig.Field('Time event\'s priority starts rising', float)
    sequenceWindowMax = pexConfig.Field('Time event\'s priority reaches maximum', float)
    sequenceWindowEnd = pexConfig.Field('Time at which event is abandoned', float)

class SequenceConfig(BaseSequenceConfig):
    sequenceFilter = pexConfig.ListField('Filter for the sequence', str)
    numSequenceExposures = pexConfig.DictField('Number of exposures per filter', str, int)

class MasterSequenceConfig(BaseSequenceConfig):
    subSequence = pexConfig.ConfigField('List of configs for sub-sequence', SequenceConfig, default=None)

class UserRegionConfig(pexConfig.Config):
    ra = pexConfig.Field('RA of region in Deg', float)
    dec = pexConfig.Field('Dec of region in Deg', float)
    diameter = pexConfig.Field('Width of region in Deg', float)

class FilterConfig(pexConfig.Config):
    name = pexConfig.Field('Name of filter', str)
    minBright = pexConfig.Field('Min V band sky brightness', float)
    maxBright = pexConfig.Field('Max V band sky brightness', float)

class DdtConfig(BaseConfig):
    sequences = pexConfig.ConfigDictField('Sequences in this proposal', int, SequenceConfig)
    masterSequences = pexConfig.ConfigDictField('Master sequences in this proposal', int,
                                                MasterSequenceConfig)
    filters = pexConfig.ConfigDictField('Filters in this proposal', str, FilterConfig)
    userRegions = pexConfig.ConfigDictField('User regions', int, UserRegionConfig)

#Continuous G sequence whatever that is
continuousG = SequenceConfig()
continuousG.name = 'continuousG'
continuousG.sequenceFilter = ['g',]
continuousG.numSequenceExposures = {'g':100}
continuousG.numSequenceEvents = 1
continuousG.numMaxMissed = 0
continuousG.sequenceInterval = 60
continuousG.sequenceWindowStart = -0.50
continuousG.sequenceWindowMax = 0.25
continuousG.sequenceWindowEnd = 0.50

G2R2sub = SequenceConfig()
G2R2sub.name = 'G2R2sub'
G2R2sub.sequenceFilter = ['g','r',]
G2R2sub.numSequenceExposures = {'g':1, 'r':1}
G2R2sub.numSequenceEvents = 45
G2R2sub.numMaxMissed = 5
G2R2sub.sequenceInterval = 16*60
G2R2sub.sequenceWindowStart = -1.0
G2R2sub.sequenceWindowMax = 1.0
G2R2sub.sequenceWindowEnd = 2.0

G2R2master = MasterSequenceConfig()
G2R2master.name = 'G2R2master'
G2R2master.subSequence = G2R2sub 
G2R2master.numSequenceEvents = 3
G2R2master.numMaxMissed = 0
G2R2master.sequenceInterval = 1*24*60*60
G2R2master.sequenceWindowStart = -0.50
G2R2master.sequenceWindowMax = 0.25
G2R2master.sequenceWindowEnd = 0.50

continuousR = SequenceConfig()
continuousR.name = 'continuousR'
continuousR.sequenceFilter = ['r',]
continuousR.numSequenceExposures = {'r':100}
continuousR.numSequenceEvents = 1
continuousR.numMaxMissed = 0
continuousR.sequenceInterval = 60
continuousR.sequenceWindowStart = -0.50
continuousR.sequenceWindowMax = 0.25
continuousR.sequenceWindowEnd = 0.50

G2R2anothersub = SequenceConfig()
G2R2anothersub.name = 'G2R2anothersub'
G2R2anothersub.sequenceFilter = ['g','r',]
G2R2anothersub.numSequenceExposures = {'g':1, 'g':1}
G2R2anothersub.numSequenceEvents = 45
G2R2anothersub.numMaxMissed = 5
G2R2anothersub.sequenceInterval = 16*60
G2R2anothersub.sequenceWindowStart = -1.0
G2R2anothersub.sequenceWindowMax = 1.0
G2R2anothersub.sequenceWindowEnd = 2.0

G2R2anothermaster = MasterSequenceConfig()
G2R2anothermaster.name = 'G2R2anothermaster'
G2R2anothermaster.subSequence = G2R2anothersub 
G2R2anothermaster.numSequenceEvents = 3
G2R2anothermaster.numMaxMissed = 0
G2R2anothermaster.sequenceInterval = 1*24*60*60
G2R2anothermaster.sequenceWindowStart = -0.50
G2R2anothermaster.sequenceWindowMax = 0.25
G2R2anothermaster.sequenceWindowEnd = 0.50

# Filter         Units: label     Format: character
# MinBrightness  Units:           Format: float; relative to v-band brightness
#                                                             and extinction
# MaxBrightness  Units:           Format: float; relative to v-band brightness
#                                                             and extinction
gFilter = FilterConfig()
gFilter.name = 'g'
gFilter.minBright = 19.0
gFilter.maxBright = 30.0

rFilter = FilterConfig()
rFilter.name = 'r'
rFilter.minBright = 19.0
rFilter.maxBright = 30.0

iFilter = FilterConfig()
iFilter.name = 'i'
iFilter.minBright = 19.0
iFilter.maxBright = 30.0

zFilter = FilterConfig()
zFilter.name = 'z'
zFilter.minBright = 17.5
zFilter.maxBright = 30.0

yFilter = FilterConfig()
yFilter.name = 'y'
yFilter.minBright = 17.5
yFilter.maxBright = 30.0

# ----------------------------------------------------------------------
#                       Field Selection Parameters
#-----------------------------------------------------------------------
#   User Region Definitions
#       list of (ra,dec,width)  containing center point around which a cone of
#                            diameter width is centered.
#       Units: deg,deg,deg Format: float, float, float
#       Default: none; do not include
########################################################################
# NOTE: DO NOT use spaces between these values or you will break config!
########################################################################
regionArr = []
regionArr.append(UserRegionConfig(ra=81.78, dec=-70.76, diameter=0.2))
regionArr.append(UserRegionConfig(ra=84.97, dec=-68.16, diameter=0.2))
regionArr.append(UserRegionConfig(ra=77.61, dec=-73.29, diameter=0.2))
regionArr.append(UserRegionConfig(ra=79.83, dec=-65.93, diameter=0.2))
regionArr.append(UserRegionConfig(ra=16.57, dec=-72.90, diameter=0.2))
regionArr.append(UserRegionConfig(ra=260.86, dec=-50.86, diameter=0.2))
regionDict = dict([(i, regionArr[i]) for i in range(len(regionArr))])

ddtConfig = DdtConfig(sequences={1:continuousG, 2:continuousR}, masterSequences={1:G2R2master, 2:G2R2anothermaster}, 
        filters={'g':gFilter, 'r':rFilter, 'i':iFilter, 'z':zFilter, 'y':yFilter}, 
        userRegions=dict([(i, regionArr[i]) for i in range(len(regionArr))]))
