#! /bin/tcsh

set machine = `uname`
if ( $machine == "Linux" ) then
    set mysql = "mysql"
    set mysqldump = "mysqldump"
else if ( $machine == "Darwin" ) then
    set mysql = "/opt/local/lib/mysql5/bin/mysql"
    set mysqldump = "/opt/local/lib/mysql5/bin/mysqldump"
endif

# Creating dat files
$mysql -u www -pzxcvbnm -e "select * from $1.Cloud" > Cloud.dat
$mysql -u www -pzxcvbnm -e "select * from $1.Seeing" > Seeing.dat
$mysql -u www -pzxcvbnm -e "select * from $1.Field" > Field.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tConfig_$2_$3" > Config_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tConfig_File_$2_$3" > Config_File_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tLog_$2_$3" > Log_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tSession_$2_$3" > Session_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tMissedHistory_$2_$3" > MissedHistory_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tObsHistory_$2_$3" > ObsHistory_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tObsHistory_Proposal_$2_$3" > ObsHistory_Proposal_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tProposal_$2_$3" > Proposal_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tProposal_Field_$2_$3" > Proposal_Field_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tSeqHistory_$2_$3" > SeqHistory_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tSeqHistory_MissedHistory_$2_$3" > SeqHistory_MissedHistory_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tSeqHistory_ObsHistory_$2_$3" > SeqHistory_ObsHistory_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tSlewActivities_$2_$3" > SlewActivities_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tSlewHistory_$2_$3" > SlewHistory_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tSlewMaxSpeeds_$2_$3" > SlewMaxSpeeds_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tSlewState_$2_$3" > SlewState_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.tTimeHistory_$2_$3" > TimeHistory_$2_$3.dat
$mysql -u www -pzxcvbnm -e "select * from $1.summary_$2_$3" > Summary_$2_$3.dat

# Gzipping
tar zcvf $2_$3_datexport.tar.gz Cloud.dat Seeing.dat Field.dat *_$2_$3.dat

# mysqldump
$mysqldump -u www -pzxcvbnm $1 tConfig_File_$2_$3 tLog_$2_$3 tTimeHistory_$2_$3 Cloud Seeing tConfig_$2_$3 tSession_$2_$3 tProposal_Field_$2_$3 Field tMissedHistory_$2_$3 tProposal_$2_$3 tSeqHistory_$2_$3 tSeqHistory_MissedHistory_$2_$3 tSeqHistory_ObsHistory_$2_$3 tObsHistory_$2_$3 tObsHistory_Proposal_$2_$3 tSlewHistory_$2_$3 tSlewState_$2_$3 tSlewActivities_$2_$3 tSlewMaxSpeeds_$2_$3 summary_$2_$3 > $2_$3_export.sql

# Gzipping
gzip -f $2_$3_export.sql
