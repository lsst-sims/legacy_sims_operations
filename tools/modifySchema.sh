#! /bin/tcsh

# Note: this calls gen_output.py, prep_opsim.py, move_data_output_obshistory.py,
#    createSQLite.py, exportSession.sh, createSubSetTables.sh and dropSubSetTables.sh

# On non-opsim Darwin machines, it seems likely that you will have to update the paths to python/mysql.

echo "####################################################################"
echo "[Checking Linux/Darwin]"
set machine = `uname`
if ( $machine == "Linux" ) then
    set python = "python"
    set mysql = "mysql"
    set mysqldump = "mysqldump"
    echo "Detected Linux machine ..."
else if ( $machine == "Darwin" ) then
    set python = "/opt/local/bin/python2.7"
    set mysql = "/opt/local/lib/mysql5/bin/mysql"
    set mysqldump = "/opt/local/lib/mysql5/bin/mysqldump"
    echo "Detected Darwin machine ..."
endif
echo "####################################################################"

echo "####################################################################"
echo "[Getting the correct hostname & tablename]"
set dbs = `mysql -u www --password=zxcvbnm --skip-column-names -e "show databases like 'OpsimDB%'"`
foreach db ($dbs)
        set sql = "select sessionHost from $db.Session where sessionID=$1"
        set hname = `mysql -u www --password=zxcvbnm --skip-column-names -e "$sql"`
        if ($hname != "") then
                        set database = $db
                        set host = $hname
        endif
end
echo "Processing simulation $host.$1"
echo "####################################################################"

# Making the Output table
echo "####################################################################"
echo "[gen_output.py]"
time $python schema_tools/gen_output.py $host $database $1
echo "####################################################################"

# Make subset of all tables
echo "####################################################################"
echo "[dropSubsetTables.sh]"
time schema_tools/dropSubsetTables.sh $database $host $1
echo "[createSubsetTables.sh]"
time schema_tools/createSubsetTables.sh $database $host $1
echo "####################################################################"

# Update the names
echo "####################################################################"
echo "[Updating the columns]"
$mysql -u www -pzxcvbnm -e "alter table $database.tObsHistory_${host}_$1 change filtSkyBright filtSkyBrightness double"
$mysql -u www -pzxcvbnm -e "alter table $database.tObsHistory_${host}_$1 change alt altitude double"
$mysql -u www -pzxcvbnm -e "alter table $database.tObsHistory_${host}_$1 change az azimuth double"
$mysql -u www -pzxcvbnm -e "alter table $database.tObsHistory_${host}_$1 add ditheredRA double"
$mysql -u www -pzxcvbnm -e "alter table $database.tObsHistory_${host}_$1 add ditheredDec double"
$mysql -u www -pzxcvbnm -e "alter table $database.tObsHistory_${host}_$1 add fiveSigmaDepth double"
#$mysql -u www -pzxcvbnm -e "alter table $database.tProposal_${host}_$1 add tag varchar(256)"
echo "####################################################################"

# Add dithering (ra, dec, night, vertex) columns & Adding indexes
echo "####################################################################"
echo "[Add dithering (ra, dec, night, vertex) columns -> prep_opsim]"
time $python schema_tools/prep_opsim.py $host $database $1
echo "####################################################################"

# Fixing visitTime & visitExpTime for tObsHistory and output tables
echo "####################################################################"
echo "[Fixing visitTime & visitExpTime]"
$mysql -u www -pzxcvbnm -e "update $database.tObsHistory_${host}_$1 set visitTime=visitExpTime"
$mysql -u www -pzxcvbnm -e "update $database.tObsHistory_${host}_$1 set visitExpTime=visitTime-4.00"
$mysql -u www -pzxcvbnm -e "update $database.summary_${host}_$1 set visitTime=visitExpTime"
$mysql -u www -pzxcvbnm -e "update $database.summary_${host}_$1 set visitExpTime=visitTime-4.00"
echo "####################################################################"

# Adding wfd tag to Proposal table for propID
#echo "####################################################################"
#echo "[Adding WFD tag]"
#$mysql -u www -pzxcvbnm -e "update $database.tProposal_${host}_$1 set tag='wfd' where propID=$2"
#echo "####################################################################"

# Copying over fiveSigmaDepth, ditheredRA, ditheredDec values from output to ObsHistory
echo "####################################################################"
echo "[Fixing fiveSigmaDepth, ditheredRA, ditheredDec values from output to ObsHistory]"
time $python schema_tools/move_data_output_obshistory.py $host $database $1
echo "####################################################################"

# Exporting session
echo "####################################################################"
echo "[Exporting session data]"
#if ($RECREATE_OUTPUT_TABLE) then
time schema_tools/exportSession.sh $database $host $1
echo "[Creating SQLite file]"
time $python schema_tools/createSQLite.py $host $1
#mv ${host}_$1_* ../output
#endif
echo "[dropSubsetTables.sh]"
time schema_tools/dropSubsetTables.sh $database $host $1
echo "####################################################################"

