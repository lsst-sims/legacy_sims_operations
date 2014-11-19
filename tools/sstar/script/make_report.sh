#! /bin/tcsh

echo "####################################################################"
echo "[make_report Config Parameters]"
# RECREATE_OUTPUT_TABLE
# 0 means it will NOT drop the output table & will not do gen_output & prep_opsim 
# 1 means it WILL drop the output table & will do gen_output & prep_opsim
set RECREATE_OUTPUT_TABLE = 1
echo "RECREATE_OUTPUT_TABLE = $RECREATE_OUTPUT_TABLE (0=don't; 1=do create output table)"
# COPY_TO_OPSIMCVS
# 0 means it will not SCP files to OPSIMCVS (files are in ../output directory)
# 1 means it will SCP files to OPSIMCVS
set COPY_TO_OPSIMCVS = 1
echo "COPY_TO_OPSIMCVS = $COPY_TO_OPSIMCVS      (0=don't; 1=do copy to opsimcvs)"
# DESIGN_STRETCH
# 0 means DESIGN
# 1 means STRETCH
set DESIGN_STRETCH = 0
echo "DESIGN_STRETCH = $DESIGN_STRETCH        (0=design; 1=stretch)"
echo "####################################################################"

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
echo "[Checking arguments]"
if ($#argv != 1) then
    echo "Usage: $0 <sessionID>"
	echo "####################################################################"
	exit
endif
echo "####################################################################"

echo "####################################################################"
echo "[Check if executables exist]"
if (-e checker && -e maketex && -e website_home && -e website_stretch && -e website_design && -e tables_visit && -e tables_coadded) then
	set ok = 1
else
	echo "[executables dont exist, will make them now]"
	cd ..
	make
	cd script
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

# Checking if ../output/design or ../output/stretch exists if not create it
echo "####################################################################"
if ($DESIGN_STRETCH) then
   set outdir = "../output/stretch"
else 
   set outdir = "../output/design"
endif
if (-e $outdir) then
   echo "[Creating output directory] [$outdir] already exists";
else
   mkdir $outdir;
   echo "[Creating output directory] [$outdir] Done";
endif
echo "####################################################################"

# Recreate output table. If you delete it, genoutput.py will automatically recreate it
echo "####################################################################"
set table = `mysql -u www --password=zxcvbnm --skip-column-names -e "use ${database}; show tables like 'output_${host}_$1';"`
if ($table == "") then 
	echo "output_${host}_$1 doesn't exist, will be created"
else
	if ($RECREATE_OUTPUT_TABLE) then
		echo "[Dropping output table and recreating]"
		time $mysql -u www --password=zxcvbnm -e "drop table ${database}.output_${host}_$1"
	endif
endif
echo "####################################################################"

# Making the Output table
echo "####################################################################"
echo "[gen_output.py]"
time $python gen_output.py $host $database $1
echo "####################################################################"

# Make subset of all tables
echo "####################################################################"
echo "[dropSubsetTables.sh]"
time ./dropSubsetTables.sh $database $host $1
echo "[createSubsetTables.sh]"
time ./createSubsetTables.sh $database $host $1
echo "####################################################################"

# Add dithering (ra, dec, night, vertex) columns & Adding indexes
echo "####################################################################"
echo "[Add dithering (ra, dec, night, vertex) columns -> prep_opsim]"
time $python prep_opsim.py $host $database $1
echo "####################################################################"

# Beginning Quick Fire Statistics file
echo "####################################################################"
echo "[starting quick fire statistics]"
echo "\\begin{table}[H]{\\textbf{Fields where Completeness is Greater than 90\% in each filter from Tables 5, 6, 7 \\& 8.}} \\\\ [1.0ex]" > ../output/${host}_$1_quickstats.tex
echo "\\begin{tabular*}{\\textwidth}{\\tblspace lllllll}" >> ../output/${host}_$1_quickstats.tex
echo "\\hline" >> ../output/${host}_$1_quickstats.tex
echo "\\hline" >> ../output/${host}_$1_quickstats.tex
echo "\\colhead{Completeness} &" >> ../output/${host}_$1_quickstats.tex
echo "\\colhead{u} &" >> ../output/${host}_$1_quickstats.tex
echo "\\colhead{g} &" >> ../output/${host}_$1_quickstats.tex
echo "\\colhead{r} &" >> ../output/${host}_$1_quickstats.tex
echo "\\colhead{i} &" >> ../output/${host}_$1_quickstats.tex
echo "\\colhead{z} &" >> ../output/${host}_$1_quickstats.tex
echo "\\colhead{y} \\\\ " >> ../output/${host}_$1_quickstats.tex
echo "\\hline" >> ../output/${host}_$1_quickstats.tex
echo "####################################################################"

# Get all the plots from checker
echo "####################################################################"
echo "[Time Summary]"
echo "[ERROR] [NEED TO work out what NOBHist is and why it is being used in TimeHistory]" > ../output/${host}_$1_timesummary.txt
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --timesummary > ../output/${host}_$1_timesummary.txt
echo "####################################################################"

echo "####################################################################"
echo "[Hour Glass]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --hourglass --plotfile=../output/${host}_$1 > ../output/${host}_$1_hourglass.txt
echo "####################################################################"

echo "####################################################################"
echo "[Opposition Plot]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --opposition --plotfile=../output/${host}_$1 > ../output/${host}_$1_opposition.txt
echo "####################################################################"

echo "####################################################################"
echo "[SixVisit Num Plots]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --sixvisitnum --plotfile=../output/${host}_$1 > ../output/${host}_$1_SixVisits.txt
echo "####################################################################"

echo "####################################################################"
echo "[Slew]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --slew --plotfile=../output/${host}_$1 > ../output/${host}_$1_slews.txt
echo "####################################################################"

echo "####################################################################"
echo "[Avg Airmass]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --airmass=1 --plotfile=../output/${host}_$1 > ../output/${host}_$1_avgairmass.txt
echo "####################################################################"

echo "####################################################################"
echo "[Max Airmass]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --airmass=0 --plotfile=../output/${host}_$1 > ../output/${host}_$1_maxairmass.txt
echo "####################################################################"

echo "####################################################################"
echo "[5sigma]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --5sigma --plotfile=../output/${host}_$1 > ../output/${host}_$1_5sigma.txt
echo "####################################################################"

echo "####################################################################"
echo "[Sky Brightness]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --skyb --plotfile=../output/${host}_$1 > ../output/${host}_$1_skyb.txt
echo "####################################################################"

echo "####################################################################"
echo "[Seeing]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --seeing --plotfile=../output/${host}_$1 > ../output/${host}_$1_seeing.txt
echo "####################################################################"

echo "####################################################################"
echo "[Revisit]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --revisits --plotfile=../output/${host}_$1 > ../output/${host}_$1_revisit_griz.txt
echo "####################################################################"

echo "####################################################################"
echo "[Completeness]"
time ./checker --hostname $host --database $database -S $1 --designstretch=$DESIGN_STRETCH --sntiming --plotfile=../output/${host}_$1 > ../output/${host}_$1_completeness.txt
echo "####################################################################"

# Create Visit Histogram Tables and the Table Visit
echo "####################################################################"
echo "[Tables Visit]"
time ./tables_visit $host $database $1 $DESIGN_STRETCH
echo "####################################################################"

# Create Coadded Table (The following call requires the --5sigma checker command to run. Dependency)
echo "####################################################################"
echo "[Tables Coadded Depth]"
time ./tables_coadded $host $1
echo "####################################################################"

# Create Frequency Distribution Histograms for airmass, skybrightness, seeing, 5sigma
echo "####################################################################"
echo "[Histograms for airmass, skybrightness, seeing & 5sigma]"
time $python histograms.py $database $1 > ../output/${host}_$1_histograms.txt
mv ${host}_$1_*.png ../output/
echo "####################################################################"

# Ending Quick Fire Statistics file
echo "####################################################################"
echo "[ending quick fire statistics]"
echo "\\hline" >> ../output/${host}_$1_quickstats.tex
echo "\\hline" >> ../output/${host}_$1_quickstats.tex
echo "\\end{tabular*}" >> ../output/${host}_$1_quickstats.tex
echo "\\caption{The 90\% numbers.}" >> ../output/${host}_$1_quickstats.tex
echo "\\label{tab:QuickFireTable}" >> ../output/${host}_$1_quickstats.tex
echo "\\end{table}" >> ../output/${host}_$1_quickstats.tex
echo "####################################################################"

# newreport.py
#echo "####################################################################"
#echo "[newreport.py]"
#time $python newreport.py $database $1 > ../output/${host}_$1_newreport.txt
#echo "####################################################################"

# summaryreport.py
echo "####################################################################"
echo "[summaryreport.py]"
time $python summaryreport.py $host $1 > ../output/${host}_$1_summaryreport.txt
head -n 9 ../output/${host}_$1_summaryreport.txt | tail -n 8 > ../output/${host}_$1_summaryreport_sec1.txt
head -n 28 ../output/${host}_$1_summaryreport.txt | tail -n 18 > ../output/${host}_$1_summaryreport_sec2.txt
echo "####################################################################"

# timereport.py
#echo "####################################################################"
#echo "[timereport.py]"
#time $python timereport.py $database $1 > ../output/${host}_$1_timereport.txt
#echo "####################################################################"

# Website creation
echo "####################################################################"
echo "[website]"
   if ($DESIGN_STRETCH) then
      time ./website_stretch $host $1 > ../output/${host}_$1_stretch.html
      #scp ../output/${host}_$1_stretch.html opsimcvs:/var/www/html/runs/${host}.$1/stretch
      #scp is already done at the end of the script
   else
      time ./website_design $host $1 > ../output/${host}_$1_design.html
      #scp ../output/${host}_$1_design.html opsimcvs:/var/www/html/runs/${host}.$1/design
      #scp is already done at the end of the script
   endif
echo "####################################################################"

# PDF tex generation
echo "####################################################################"
echo "[pdf generation for revisit, timesummary, newreport]"
echo "\\begin{verbatim}" > ../output/${host}_$1_revisit_griz.tex
cat ../output/${host}_$1_revisit_griz.txt >> ../output/${host}_$1_revisit_griz.tex
echo "\\end{verbatim}" >> ../output/${host}_$1_revisit_griz.tex
echo "\\begin{verbatim}" > ../output/${host}_$1_timesummary.tex
cat ../output/${host}_$1_timesummary.txt >> ../output/${host}_$1_timesummary.tex
echo "\\end{verbatim}" >> ../output/${host}_$1_timesummary.tex
# The tex file for this section is now being created in the visits.c file
#echo "\\begin{verbatim}" > ../output/${host}_$1_SixVisits.tex
#cat ../output/${host}_$1_SixVisits.txt >> ../output/${host}_$1_SixVisits.tex
#echo "\\end{verbatim}" >> ../output/${host}_$1_SixVisits.tex
#echo "{\\small" > ../output/${host}_$1_newreport_top.tex
#echo "\\begin{verbatim}" > ../output/${host}_$1_newreport_top.tex
#head -n 26 ../output/${host}_$1_newreport.txt >> ../output/${host}_$1_newreport_top.tex
#echo "\\end{verbatim}" >> ../output/${host}_$1_newreport_top.tex
#echo "}" >> ../output/${host}_$1_newreport_top.tex
echo "####################################################################"

# generate .tex file
echo "####################################################################"
echo "[maketex]"
time ./maketex $host $database $1 $DESIGN_STRETCH
echo "####################################################################"

#substitute SCPgalactic.conf fo SGPgalactic.conf - hack
#appears in 2 tables - this fix is not be extensible
echo "####################################################################"
echo "[SGPgalactic -> SCPgalactic fix]"
cp ../output/${host}_$1_sstar.tex ../output/tmp
sed s/SGPgalactic/SCPgalactic/g < ../output/tmp > ../output/${host}_$1_sstar.tex
rm ../output/tmp
cp ../output/${host}_$1_VisitsTable.tex ../output/tmp
sed s/SGPgalactic/SCPgalactic/g < ../output/tmp > ../output/${host}_$1_VisitsTable.tex
rm ../output/tmp
echo "####################################################################"

# create pdf
echo "####################################################################"
echo "[pdflatex]"
pdflatex ../output/${host}_$1_sstar.tex > ../output/${host}_$1_sstar.pdflog
pdflatex ../output/${host}_$1_sstar.tex >> ../output/${host}_$1_sstar.pdflog
pdflatex ../output/${host}_$1_sstar.tex >> ../output/${host}_$1_sstar.pdflog
mv ${host}_$1_* ../output
echo "####################################################################"

# Creating the output files
echo "####################################################################"
echo "[Creating DAT file]"
time $mysql -u www --password=zxcvbnm -e "select * from ${database}.output_${host}_$1" > ../output/${host}_$1_output.dat
echo "[Creating SQL file]"
time $mysqldump -u www --password=zxcvbnm $db output_${host}_$1 > ../output/${host}_$1_output.sql
echo "[gzip DAT file]"
time gzip -f ../output/${host}_$1_output.dat
echo "[gzip SQL file]"
time gzip -f ../output/${host}_$1_output.sql
echo "####################################################################"

# Exporting session
echo "####################################################################"
echo "[Exporting session data]"
#if ($RECREATE_OUTPUT_TABLE) then
time ./exportSession.sh $database $host $1
echo "[Creating SQLite file]"
time $python createSQLite.py $host $1
mv ${host}_$1_* ../output
#endif
echo "[dropSubsetTables.sh]"
time ./dropSubsetTables.sh $database $host $1
echo "####################################################################"

# Moving files to final output directory
echo "####################################################################"
echo "[Moving files to output directory]"
mv ../output/${host}_$1_* $outdir
echo "####################################################################"

# Creating top level webpage for opsimcvs
echo "####################################################################"
echo "[Creating top or home level webpage for opsimcvs]"
time ./website_home $host $1 > ../output/${host}.$1.html
echo "####################################################################"

# Changing Permissions on output files
echo "####################################################################"
echo "[Changing permissions for output files]"
#chmod 775 $outdir
#chmod 664 ../output/${host}.$1.html
#chmod 664 $outdir/${host}_$1*
echo "####################################################################"

# Copying files to opsimcvs
if ($COPY_TO_OPSIMCVS) then
   echo "####################################################################"
   echo "[Moving files to opsimcvs]"
   set fslash = "/"
   set outdir2 = ${outdir}${fslash}
   echo "Copying to $outdir2${host}_$1_*"
   if ($DESIGN_STRETCH) then
      scp ${outdir2}${host}_$1_* opsimcvs:/var/www/html/runs/${host}.$1/stretch
   else 
      scp ${outdir2}${host}_$1_* opsimcvs:/var/www/html/runs/${host}.$1/design
   endif
   scp ../output/${host}.$1.html opsimcvs:/var/www/html/runs/${host}.$1
   echo "####################################################################"
endif

