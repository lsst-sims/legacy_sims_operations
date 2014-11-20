#! /bin/tcsh

set machine = `uname`
if ( $machine == "Linux" ) then
    set mysql = "mysql"
    set mysqldump = "mysqldump"
else if ( $machine == "Darwin" ) then
    set mysql = "/opt/local/lib/mysql5/bin/mysql"
    set mysqldump = "/opt/local/lib/mysql5/bin/mysqldump"
endif

# Dropping tables
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tConfig_File_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tLog_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tTimeHistory_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tConfig_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tSession_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tProposal_Field_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tMissedHistory_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tProposal_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tSeqHistory_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tSeqHistory_MissedHistory_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tSeqHistory_ObsHistory_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tObsHistory_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tObsHistory_Proposal_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tSlewHistory_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tSlewActivities_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tSlewState_$2_$3"
$mysql -u www -pzxcvbnm -e "drop table if exists $1.tSlewMaxSpeeds_$2_$3"

# Removing dat files
rm *_$2_$3.dat
