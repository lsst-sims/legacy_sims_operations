void processArgs(int argc, char **argv) {
  int nerrors, i;
  char *savptr, str[1024], *str1, machName[1024], sessIDstr[1024];

  struct arg_str *arg_sessionID     = arg_str1(  "S",    "sessionID",    "<mach.sessionID>", "session ID of run to be processed\n");
  struct arg_str *arg_propIDs       = arg_str0(  "P",    "proposals", "<int [,int [,int]]>", "quoted string of proposal numbers to use\n");
  struct arg_str *arg_skipDays      = arg_str0(  "D",         "days",    "<skip [,length]>", "skip days at start, do length days after\n");
  struct arg_lit *arg_Check         = arg_lit0( NULL,     "checkobs",                        "check observations for basic errors\n");
  struct arg_lit *arg_TimeSummary   = arg_lit0( NULL,  "timesummary",                        "time summary");
  struct arg_lit *arg_PeriodSearch  = arg_lit0( NULL, "periodsearch",                        "make periodogram plots\n");
  struct arg_lit *arg_Hourglass     = arg_lit0(  "H",    "hourglass",                        "make hourglass plot\n");
  struct arg_lit *arg_Opposition    = arg_lit0( NULL,   "opposition",                        "make solar angle (opposition) plot\n");
  struct arg_str *arg_Airmass       = arg_str0( NULL,      "airmass",               "<int>", "make per-field airmass plot (0 is max, 1 is median)\n");
  struct arg_lit *arg_SixVisits     = arg_lit0(  "V",  "sixvisitnum",                        "make all-filter visit numbers plot\n");
  struct arg_lit *arg_5sigma	    = arg_lit0(  "V",  "5sigma",                             "make aitoff plot for median 5sigma also per proposal\n");
  struct arg_lit *arg_skyb          = arg_lit0(  "V",  "skyb",                               "make aitoff plot for median skyb also per proposal\n");
  struct arg_lit *arg_seeing        = arg_lit0(  "V",  "seeing",                             "make aitoff plot for median seeing also per proposal\n");
  struct arg_lit *arg_Visits        = arg_lit0(  "v",     "visitnum",                        "make visit numbers plot for specified filters\n \
                                                (requires -f|--filters)\n");
  struct arg_str *arg_reqFilters    = arg_str0(  "f",      "filters",       "<f [,f [,f]]>", "which filters to use; f in {ugrizy}\n");
  struct arg_lit *arg_NEOrevisits   = arg_lit0(  "R",     "revisits",                        "make NEO revisit numbers plot\n");
  struct arg_lit *arg_Slew          = arg_lit0( NULL,         "slew",                        "make slew time histogram\n");
  struct arg_lit *arg_SNtiming      = arg_lit0( NULL,     "sntiming",                        "make SN Ia cadence plots\n");
  struct arg_file *arg_plotfileRoot = arg_file0(NULL,     "plotfile",        "harcopy file", "root name of plotfile for hardcopy\n");
  struct arg_file *arg_plotTitle    = arg_file0(NULL,    "plottitle",            "<string>", "title for plots\n");
  struct arg_lit *arg_help          = arg_lit0(  "h",         "help",                        "show usage\n");
  struct arg_lit *arg_debug         = arg_lit0(  "d",        "debug",                        "debugging output\n");
  struct arg_str *arg_hostname      = arg_str1(  "N",     "hostname",            "<string>", "if you know hostname \n");
  struct arg_str *arg_databasename  = arg_str1(  "DB",     "database",            "<string>", "if you know the db name \n");
  struct arg_str *arg_designstretch = arg_str1( NULL,     "designstretch",         "<int>", "design or stretch value\n");
  struct arg_end *arg_endp          = arg_end(20);

  void *argtable[] = {arg_sessionID, arg_propIDs,      arg_skipDays,    arg_TimeSummary, arg_Check,     arg_PeriodSearch,
                      arg_Hourglass, arg_Opposition,   arg_Airmass,     arg_SixVisits, arg_5sigma, arg_skyb, arg_seeing, 
                      arg_Slew, arg_Visits, arg_reqFilters,   arg_NEOrevisits, arg_SNtiming,  arg_plotfileRoot,
                      arg_plotTitle, arg_debug, arg_help, arg_hostname, arg_designstretch, arg_databasename, arg_endp};


  if (arg_nullcheck(argtable) != 0) fprintf(stderr, "error: insufficient memory\n");

  nerrors = arg_parse(argc,argv,argtable);

  // process arguments

  // render assistance when asked
  if(arg_help->count>0) {
    fprintf(stderr,"Usage: %s [options]\n     where [options] are:\n\n",argv[0]);
    arg_print_glossary(stderr, argtable, "%-45s  %s");
    //    arg_print_syntaxv(stderr, argtable, "\n");
    exit(1);
  }

  // list errors
  if (nerrors > 0) {
    arg_print_errors(stdout,arg_endp,argv[0]);
    fprintf(stderr,"\nUsage: %s [options]\n     where [options] are:\n\n",argv[0]);
    arg_print_glossary(stderr, argtable, "%-45s  %s");
    //    arg_print_syntaxv(stderr, argtable, "\n");
    exit(1);
  }

  // set database tableName and sessionID from sessionID argument
  //strcpy(str, *arg_sessionID->sval);
  //strcpy(machName, strtok_r(str,".",&savptr));
  //strcpy(sessIDstr, strtok_r(NULL,".",&savptr));
  strcpy(sessIDstr, *arg_sessionID->sval);
  sessionID = atoi(sessIDstr);

  if ( *arg_databasename->sval == NULL ) {
	sprintf(database, "%s", "OpsimDB");
  } else {
	sprintf(database, "%s", *arg_databasename->sval);
  }

  if ( *arg_hostname->sval == NULL ) {
	if ( gethostname(identifier, identifier_length) == 0 ) {
		sprintf(hostname, "%s", identifier);
	} else {
		printf( "Hostname : %s\n", strerror(errno));
		exit(1);
	}
  } else {
	sprintf (hostname, "%s", *arg_hostname->sval);
  }
  sprintf(tableName, "output_%s_%d", hostname, sessionID);
  // set action flags

  if(arg_5sigma->count>0) do5sigma=1;
  if(arg_skyb->count>0) doskyb=1;
  if(arg_seeing->count>0) doSeeing=1;
  if(arg_TimeSummary->count>0) doTimeSummary=1;
  if(arg_Check->count>0) doCheck=1;
  if(arg_PeriodSearch->count>0) doPeriodSearch=1;
  if(arg_Hourglass->count>0) doHourglass=1;
  if(arg_Opposition->count>0) doOpposition=1;
  if(arg_designstretch->count>0) {
	if ( strcmp(*arg_designstretch->sval, "0") == 0) {
		useDesignStretch = 0;
	} else {
		useDesignStretch = 1;
    }
  } 
  if(arg_Airmass->count>0) {
    doAirmass=1;
    if(strcmp(*arg_Airmass->sval, "0") != 0) {
	useMaxAirmass=0; 
    }
    else  {
	useMaxAirmass=1;
    }	
  }
  if(arg_SixVisits->count>0) doSixVisits=1;
  if(arg_Visits->count>0) {
    doVisits=1;
    if(arg_reqFilters->count==0) {
      fprintf(stderr,"Error: with -v|--visitsnum must give -f|--filters\n");
      exit(1);
    }
    strcpy(str, *arg_reqFilters->sval);
    i = 0;
    strcpy(desiredFilters[i],strtok_r(str," ,",&savptr));
    i++;
    while((str1=strtok_r(NULL," ,",&savptr))!= NULL) {
      strcpy(desiredFilters[i],str1);
      i++;
    }
    ndesiredFilters = i;
  }
  if(arg_NEOrevisits->count>0) doNEOrevisits=1;
  if(arg_SNtiming->count>0) doSNtiming=1;
  if(arg_Slew->count>0) doSlew=1;
  if(arg_propIDs->count>0) {
    strcpy(str, *arg_propIDs->sval);
    i = 0;
    propIDs[i] = atoi(strtok_r(str," ,",&savptr));
    i++;
    while((str1=strtok_r(NULL," ,",&savptr))!= NULL) {
      propIDs[i] = atoi(str1);
      i++;
    }
    nIDs = i;
  }
  if(arg_plotfileRoot->count>0) {
    strcpy(plotfileRoot,arg_plotfileRoot->filename[0]);
    doHardcopy = 1;
  }
  if(arg_plotTitle->count>0) {
    strcpy(plotTitle,arg_plotTitle->filename[0]);
  }
  if(arg_skipDays->count>0) {
    strcpy(str, *arg_skipDays->sval);
    skipDays = atoi(strtok_r(str," ,",&savptr));
    str1 = strtok_r(NULL," ,",&savptr);
    if(str1 != (char *) NULL) lengthDays = atoi(str1);    
  }
  if(arg_debug->count>0) {
    debug = 1;
  }

#if 0
  printf("     sessionID: %d\n", sessionID);
  printf("      skipDays: %d\n", skipDays);
  printf("    lengthDays: %d\n", lengthDays);
  printf("          nIDs: %d\n", nIDs);
  if(nIDs>0) {
    printf("     using IDs: ");  for(i=0; i<nIDs; i++) printf(" %d",propIDs[i]); printf("\n");
  }

  printf("       doCheck: %d\n", doCheck);
  printf("doPeriodSearch: %d\n", doPeriodSearch);
  printf("   doHourglass: %d\n", doHourglass);
  printf("   doOpposition: %d\n", doOpposition);
  printf("   doSixVisits: %d\n", doSixVisits);
  printf("      doVisits: %d\n", doVisits);
  if(doVisits) {
    printf(" using filters: "); for(i=0; i<ndesiredFilters; i++) printf(" %s",desiredFilters[i]); printf("\n");
  }
  printf(" doNEOrevisits: %d\n", doNEOrevisits);
  printf("    doSNtiming: %d\n", doSNtiming);
  if(strlen(plotfileRoot)>0) printf(" hardcopy file: \"%s\"\n", plotfileRoot);
  if(strlen(plotTitle)>0) printf("    plot title: \"%s\"\n", plotTitle);
  printf("         debug: %d\n", debug);
#endif

  arg_freetable(argtable,sizeof(argtable)/sizeof(argtable[0]));
}
