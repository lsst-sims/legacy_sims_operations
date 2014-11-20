
// the connection
MYSQL mysql;

// utility macros
#define mysqlError(arg) {fprintf(stderr,"mysql error executing \"%s\": %s\n", arg, mysql_error(&mysql));}
#define doQuery(arg)  if(mysql_exec_sql(&mysql, arg)) { mysqlError(arg); exit(1); }

// open a connexion to the database
void ConnectToMySQL(void) {
  if(!mysql_init(&mysql)) {
    printf("\nFailed to initate MySQL connection");
    exit(1);
  }
  else {
    //    printf("initiated connection\n");
  }
}

// login to the database
void LoginToMySQL(char *host, char *user, char *passwd) {
  if (!mysql_real_connect(&mysql,host,user,passwd,NULL,0,NULL,0)) {
    printf( "Failed to connect: Error: %s\n", mysql_error(&mysql));
    exit(1);
  }
  else {
    //    printf("logged in\n");
  }
}

// do a query helper function
int mysql_exec_sql(MYSQL *mysql,const char *create_definition) {
  return mysql_real_query(mysql,create_definition,strlen(create_definition));
}

// read obsHistory information
//  use the data from the nIDs proposal IDs in propIDs
//  use data with startMJD <= expMJD <= endMJD
//  sort the data by the field name in orderBy if not empty
//  use the table within LSST in tableName
//  allocate space for resulting data and store data, returning in data
//  and length in len
void read_obsHistory(int *propIDs, int nIDs,
                     double startMJD, double endMJD,
                     char *orderBy,
                     int sessionID, char *tableName,
                     observation **data, int *len) {
  int i, k, flag;
  int select_on_ids, select_on_dates;
  MYSQL_STMT *stmt;
  MYSQL_BIND bind[16];
  observation obsbuf, *myobs;
  my_bool error[16];
  char select[1024], tmpstr[1024];

  //fprintf(stderr,"forming query..");

  // prepare the query string
  strcpy(select,"SELECT ");
  strcat(select,"obsHistID, fieldRA, fieldDec, slewTime, slewDist, expMJD, expDate, finSeeing, vSkyBright,");
  strcat(select,"filtSkyBright, fivesigma, perry_skybrightness, fivesigma_ps, fieldID, filter, propID FROM ");
  strcat(select, tableName);
  sprintf(tmpstr, " WHERE sessionID = %d ",sessionID);
  strcat(select, tmpstr);

  select_on_ids = (nIDs>0) && (nIDs < numAllIDs);

  if(select_on_ids) strcat(select," AND ");

  if(select_on_ids) {
    strcat(select," ( ");
    for(i=0; i<nIDs; i++) {
      sprintf(tmpstr, " propID = %d ", propIDs[i]);
      strcat(select,tmpstr);
      if(i!=nIDs-1) strcat(select," OR ");
    }
    strcat(select," ) ");
  }
  
  select_on_dates = !( ((startMJD==0.0) && (endMJD==0.0)) );
  if(select_on_dates) strcat(select," AND ");

  if(select_on_dates) {
    strcat(select," ( ");
    sprintf(tmpstr," expMJD >= %f AND expMJD <= %f ", startMJD, endMJD);
    strcat(select,tmpstr);
    strcat(select," ) ");
  }

  if(strlen(orderBy)>0) {
    sprintf(tmpstr," ORDER BY %s", orderBy);
    strcat(select,tmpstr);
  }

  strcat(select,";");
  //printf("[[[[[[sql]]]]]] : %s\n", select);
  
  if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
    fprintf(stderr,"error in mysql_stmt_init: %s\n",mysql_stmt_error(stmt));
    exit(1);
  }

  flag = mysql_stmt_prepare(stmt, select, strlen(select));
  if(flag!=0) {
    fprintf(stderr,"error in mysql_stmt_prepare: %s\n",mysql_stmt_error(stmt));
    exit(1);
  }

  memset(bind, 0, sizeof(bind));

  i = 0;
  bind[i].buffer_type = FIELD_TYPE_LONG;
  bind[i].buffer = &(obsbuf.obsHistID);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.ra);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.dec);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.slewtime);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.slewdist);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.date);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_LONG;
  bind[i].buffer = &(obsbuf.expdate);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.seeing);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.vskybright);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.filtsky);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.m5);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.etc_skyb);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_DOUBLE;
  bind[i].buffer = &(obsbuf.etc_m5);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_LONG;
  bind[i].buffer = &(obsbuf.field);
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_STRING;
  bind[i].buffer = &(obsbuf.filtername);
  bind[i].buffer_length = 10;
  bind[i].error = &error[i];
  i++;
  bind[i].buffer_type = FIELD_TYPE_LONG;
  bind[i].buffer = &(obsbuf.propid);
  bind[i].error = &error[i];
  i++;

  flag = mysql_stmt_bind_result(stmt, bind);
  if(flag!=0) {
    fprintf(stderr, "error in mysql_stmt_bind_result: %s", mysql_stmt_error(stmt));
    exit(1);
  }

  //fprintf(stderr,"executing query..");

  flag = mysql_stmt_execute(stmt);
  if(flag!=0) {
    fprintf(stderr, "error in mysql_stmt_execute: %s", mysql_stmt_error(stmt));
    exit(1);
  }

  //fprintf(stderr,"executed query..");

  flag = mysql_stmt_store_result(stmt);
  if(flag!=0) {
    fprintf(stderr, "error in mysql_stmt_store_result: %s", mysql_stmt_error(stmt));
    exit(1);
  }

  //fprintf(stderr,"stored result..");
  
  *len = mysql_stmt_num_rows(stmt);
  //fprintf(stderr,"allocating space for %d visits\n", *len);
  if( (myobs = malloc( (*len)*sizeof(observation) ) ) == (observation *) NULL) {
    fprintf(stderr,"error: couldn't allocate memory for observations\n");
    exit(1);
  }

  //fprintf(stderr,"reading %d visits..", *len);
                
  i = 0;
  flag = 0;
  while(flag==0) {
    flag = mysql_stmt_fetch(stmt);
    if(flag!=0) {
      if(flag == MYSQL_NO_DATA) {
        //fprintf(stderr,"done fetching data..");
        flag = 1;
      }
      else if(flag == MYSQL_DATA_TRUNCATED) {
        flag = 1;
        for(k=0; k<10; k++) {
          if(error[k]!=0) printf("fetching data truncated in parameter %d\n",k);
        }
      }
      else {
        fprintf(stderr, "error in mysql_stmt_fetch: %s\n", mysql_stmt_error(stmt));
        exit(1);
      }
    }
    if(flag==0) {
      myobs[i] = obsbuf;
      i++;
    }
  }

  mysql_stmt_close(stmt);

  *data = myobs;
  //fprintf(stderr,"done\n");
}

void get_startendMJD(double *start, double *end, int sessionID, char *tableName) {
  char tmpstr[1024];
  MYSQL_RES *result;
  MYSQL_ROW row;

  sprintf(tmpstr,"SELECT MIN(expMJD), MAX(expMJD) FROM %s WHERE sessionID = %d;\n",
          tableName, sessionID);
  doQuery(tmpstr);
  result = mysql_store_result(&mysql);
  if(result) {
    row=mysql_fetch_row(result);
    sscanf(row[0],"%lf",start);
    sscanf(row[1],"%lf",end);
    mysql_free_result(result);
  }
  else {
    fprintf(stderr,"error in get_startendMJD: nothing returned by query: %s\n", tmpstr);
    exit(1);
  }

}

void get_numFields(int *numFields, int sessionID, char *tableName) {
  char tmpstr[1024];
  MYSQL_RES *result;
  MYSQL_ROW row;

  sprintf(tmpstr,"SELECT DISTINCT fieldID from %s WHERE sessionID = %d;\n",
          tableName, sessionID);
  doQuery(tmpstr);
  result = mysql_store_result(&mysql);

  if(result) {
    *numFields = mysql_num_rows(result);
    mysql_free_result(result);
  }
  else {
    fprintf(stderr,"error in get_numFields: nothing returned by query: %s\n", tmpstr);
    exit(1);
  }
}

void get_propIDs(int *propIDs, int *nIDs, int sessionID, char *tableName) {
  char tmpstr[1024];
  MYSQL_RES *result;
  MYSQL_ROW row;

  sprintf(tmpstr,"select distinct propID from %s WHERE sessionID = %d ORDER BY propID;",
          tableName, sessionID);
  //  printf("%s\n", tmpstr);
  doQuery(tmpstr);
  result = mysql_store_result(&mysql);
  if(result) {
    *nIDs = 0;
    while((row=mysql_fetch_row(result)) != NULL) {
      sscanf(row[0],"%d",&(propIDs[*nIDs]));
      (*nIDs)++;
    }
    mysql_free_result(result);
  }
  else {
    fprintf(stderr,"error in get_propIDs: no propID's returned by query: %s\n", tmpstr);
    exit(1);
  }

}

void openLSSTdb(char *host, char *user, char *passwd, char *database) {
  char tmpstr[1024];

  ConnectToMySQL();
  LoginToMySQL(host,user,passwd);
  sprintf(tmpstr, "use %s",database);
  doQuery(tmpstr);
}

void closeLSSTdb(void) {
  mysql_close(&mysql);
}

#if 0
#define LENMAX 1000000
int main(int argc, char **argv) {
  int len, i;
  observation visits[LENMAX];
  int propIDs[10], nIDs, sessionID=10;
  char *tableName = "output_10";
  double start, end;

  openLSSTdb();

  get_propIDs(propIDs,&nIDs,sessionID,tableName);
  printf("found propIDs: ");
  for(i=0; i<nIDs; i++) printf("%d ",propIDs[i]);
  printf("\n");
  numprops = nIDs;

  get_startendMJD(&start, &end, sessionID, tableName);
  printf("from %f to %f\n", start, end);

  //  read_obsHistory(propIDs, nIDs, start, end, "expMJD", tableName);
  read_obsHistory(propIDs, nIDs, start, end, "", sessionID, tableName);
  printf("read %d visits\n", numobs);
  printf("obs[1].fieldID = %d\n", obs[1].field);

  closeLSSTdb();

}
#endif

