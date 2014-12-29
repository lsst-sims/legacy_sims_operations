#! /bin/tcsh

set mysql = "mysql"

set mysqlcmd = "$mysql -u www"
if ( ! -f $HOME/.my.cnf ) then
  set mysqlcmd = "$mysqlcmd --password=zxcvbnm"
endif

# Creating table from sessionID
echo "Creating table from sessionID"
$mysqlcmd -e "create table $1.tConfig_File_$2_$3 like $1.Config_File"
$mysqlcmd -e "create table $1.tLog_$2_$3 like $1.Log"
$mysqlcmd -e "create table $1.tTimeHistory_$2_$3 like $1.TimeHistory"
$mysqlcmd -e "create table $1.tConfig_$2_$3 like $1.Config"
$mysqlcmd -e "create table $1.tSession_$2_$3 like $1.Session"
$mysqlcmd -e "create table $1.tProposal_Field_$2_$3 like $1.Proposal_Field"
$mysqlcmd -e "create table $1.tMissedHistory_$2_$3 like $1.MissedHistory"
$mysqlcmd -e "create table $1.tProposal_$2_$3 like $1.Proposal"
$mysqlcmd -e "create table $1.tSeqHistory_$2_$3 like $1.SeqHistory"
$mysqlcmd -e "create table $1.tSeqHistory_MissedHistory_$2_$3 like $1.SeqHistory_MissedHistory"
$mysqlcmd -e "create table $1.tSeqHistory_ObsHistory_$2_$3 like $1.SeqHistory_ObsHistory"
$mysqlcmd -e "create table $1.tObsHistory_$2_$3 like $1.ObsHistory"
$mysqlcmd -e "create table $1.tObsHistory_Proposal_$2_$3 like $1.ObsHistory_Proposal"
$mysqlcmd -e "create table $1.tSlewHistory_$2_$3 like $1.SlewHistory"
$mysqlcmd -e "create table $1.tSlewActivities_$2_$3 like $1.SlewActivities"
$mysqlcmd -e "create table $1.tSlewState_$2_$3 like $1.SlewState"
$mysqlcmd -e "create table $1.tSlewMaxSpeeds_$2_$3 like $1.SlewMaxSpeeds"

# Inserting table from sessionID
echo "Inserting data from sessionID"
$mysqlcmd -e "insert into $1.tConfig_File_$2_$3 select * from $1.Config_File where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tLog_$2_$3 select * from $1.Log where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tTimeHistory_$2_$3 select * from $1.TimeHistory where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tConfig_$2_$3 select * from $1.Config where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tSession_$2_$3 select * from $1.Session where sessionID=$3"
$mysqlcmd -e "insert into $1.tProposal_Field_$2_$3 select * from $1.Proposal_Field where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tMissedHistory_$2_$3 select * from $1.MissedHistory where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tProposal_$2_$3 select * from $1.Proposal where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tSeqHistory_$2_$3 select * from $1.SeqHistory where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tSeqHistory_MissedHistory_$2_$3 select * from $1.SeqHistory_MissedHistory where MissedHistory_Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tSeqHistory_ObsHistory_$2_$3 select * from $1.SeqHistory_ObsHistory where ObsHistory_Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tObsHistory_$2_$3 select * from $1.ObsHistory where Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tObsHistory_Proposal_$2_$3 select * from $1.ObsHistory_Proposal where ObsHistory_Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tSlewHistory_$2_$3 select * from $1.SlewHistory where ObsHistory_Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tSlewActivities_$2_$3 select $1.SlewActivities.* from $1.SlewActivities join $1.SlewHistory where $1.SlewHistory.slewID=$1.SlewActivities.SlewHistory_slewID and $1.SlewHistory.ObsHistory_Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tSlewState_$2_$3 select $1.SlewState.* from $1.SlewState join $1.SlewHistory where $1.SlewHistory.slewID=$1.SlewState.SlewHistory_slewID and $1.SlewHistory.ObsHistory_Session_sessionID=$3"
$mysqlcmd -e "insert into $1.tSlewMaxSpeeds_$2_$3 select $1.SlewMaxSpeeds.* from $1.SlewMaxSpeeds join $1.SlewHistory where $1.SlewHistory.slewID=$1.SlewMaxSpeeds.SlewHistory_slewID and $1.SlewHistory.ObsHistory_Session_sessionID=$3"
