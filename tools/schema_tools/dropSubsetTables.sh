#! /bin/tcsh

set mysql = "mysql"

set mysqlcmd = "$mysql -u www"
if ( ! -f $HOME/.my.cnf ) then
  set mysqlcmd = "$mysqlcmd --password=zxcvbnm"
endif

# Dropping tables
$mysqlcmd -e "drop table if exists $1.tConfig_File_$2_$3"
$mysqlcmd -e "drop table if exists $1.tLog_$2_$3"
$mysqlcmd -e "drop table if exists $1.tTimeHistory_$2_$3"
$mysqlcmd -e "drop table if exists $1.tConfig_$2_$3"
$mysqlcmd -e "drop table if exists $1.tSession_$2_$3"
$mysqlcmd -e "drop table if exists $1.tProposal_Field_$2_$3"
$mysqlcmd -e "drop table if exists $1.tMissedHistory_$2_$3"
$mysqlcmd -e "drop table if exists $1.tProposal_$2_$3"
$mysqlcmd -e "drop table if exists $1.tSeqHistory_$2_$3"
$mysqlcmd -e "drop table if exists $1.tSeqHistory_MissedHistory_$2_$3"
$mysqlcmd -e "drop table if exists $1.tSeqHistory_ObsHistory_$2_$3"
$mysqlcmd -e "drop table if exists $1.tObsHistory_$2_$3"
$mysqlcmd -e "drop table if exists $1.tObsHistory_Proposal_$2_$3"
$mysqlcmd -e "drop table if exists $1.tSlewHistory_$2_$3"
$mysqlcmd -e "drop table if exists $1.tSlewActivities_$2_$3"
$mysqlcmd -e "drop table if exists $1.tSlewState_$2_$3"
$mysqlcmd -e "drop table if exists $1.tSlewMaxSpeeds_$2_$3"

# Removing dat files
rm *_$2_$3.dat Cloud.dat Seeing.dat Field.dat
