#include <strings.h>

struct config {
	int configID;
	int sessionID;
	int propID;
	char moduleName[256];
	int paramIndex;
	char paramName[256];
	char paramValue[256];
	char comment[256];
};

struct session {
	int sessionID;
	char sessionUser[256];
	char sessionHost[256];
	char sessionDate[256];
	char version[20];
	char runComment[256];
};

struct proposal {
	int propID;
	char propName[256];
	char propConf[256];
	double priority;
	int nUserRegions;
    char lookahead[256];
};

struct field {
	int fieldID;
	double fieldFov;
	double fieldRA;
	double fieldDec;
	double fieldGL;
	double fieldGB;
	double fieldEL;
	double fieldEB;
};

struct field_query_data {
	char filter[16];
	int count;
};


char hostname[80];
char identifier[80];
int identifier_length = 80;
char s[1024];
int sessionID;
MYSQL mysql;
struct config config_data[10000];
int config_data_length;
struct session session_data;
struct proposal proposal_list[100];
int proposal_list_length;
struct field field_data[6000];
int field_data_length;
int useDesignStretch;

double observation_datafield[5000000];
int observation_datafield_length;

struct field_query_data filter_datafield[6];
int filter_datafield_length;

FILE* fp;

#define write(arg) fprintf(fp, "%s\n", arg);

// utility macros
#define mysqlError(arg) {fprintf(stderr,"mysql error executing \"%s\": %s\n", arg, mysql_error(&mysql));}
#define doQuery(arg)  if(mysql_exec_sql(&mysql, arg)) { mysqlError(arg); exit(1); }

// do a query helper function
int mysql_exec_sql(MYSQL *mysql,const char *create_definition) {
	return mysql_real_query(mysql,create_definition,strlen(create_definition));
}

// open a connexion to the database
void ConnectToMySQL(void) {
	if(!mysql_init(&mysql)) {
		printf("\nFailed to initate MySQL connection");
		exit(1);
	}
	else {
		//printf("initiated connection\n");
	}
}

// login to the database
void LoginToMySQL(char *host, char *user, char *passwd) {
	if (!mysql_real_connect(&mysql,host,user,passwd,NULL,0,NULL,0)) {
		printf( "Failed to connect: Error: %s\n", mysql_error(&mysql));
		exit(1);
	}
	else {
		//printf("logged in\n");
	}
}

void openLSSTdb(char *host, char *user, char *passwd, char *database) {
	char tmpstr[1024];
	ConnectToMySQL();
	LoginToMySQL(host,user,passwd);
	sprintf(tmpstr, "use %s",database);
	doQuery(tmpstr);
}

void closeLSSTdb() {
	mysql_close(&mysql);
}

void readConfigData() {
	int i, k, flag;
	char sql[1024];
	
	sprintf(sql, "select configID, Session_sessionID as sessionID, nonPropID, moduleName, paramIndex, paramName, paramValue, comment from Config where Session_sessionID=%d;", sessionID);

	MYSQL_STMT *stmt;
	MYSQL_BIND bind[8];
	my_bool error[8];
	
	struct config cbuffer;

	//fprintf(stderr , "forming query..");
	if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
		fprintf(stderr,"error in mysql_stmt_init: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	flag = mysql_stmt_prepare(stmt, sql, strlen(sql));
	if(flag!=0) {
		fprintf(stderr,"error in mysql_stmt_prepare: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	memset(bind, 0, sizeof(bind));

	i = 0;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(cbuffer.configID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(cbuffer.sessionID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(cbuffer.propID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(cbuffer.moduleName);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(cbuffer.paramIndex);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(cbuffer.paramName);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(cbuffer.paramValue);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(cbuffer.comment);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	
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
	config_data_length = mysql_stmt_num_rows(stmt);
	//fprintf(stderr,"reading %d config_data..", config_data_length);

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
			memcpy(&(config_data[i]), &(cbuffer), sizeof(struct config));
			i++;
		}
	}
	
	mysql_stmt_close(stmt);
	//fprintf(stderr,"done\n");

	/*for(i=0; i < config_data_length; i++) {
		printf("%d %d %d %s %d %s %s %s\n",
			config_data[i].configID,
			config_data[i].sessionID,
			config_data[i].propID,
			config_data[i].moduleName,
			config_data[i].paramIndex,
			config_data[i].paramName,
			config_data[i].paramValue,
			config_data[i].comment);
	}*/
}

char* getConfigValue(char* pName) {
	int i;
	for(i=0; i < config_data_length; i++) {
		if ( strcmp(config_data[i].paramName, pName) == 0 ) {
			return config_data[i].paramValue;
		}
	}
	return "?";
}

char* getProposalValue(char* pName, int propID) {
	int i;
	for(i=0; i < config_data_length; i++) {
		if ( strcmp(config_data[i].paramName, pName) == 0 && propID == config_data[i].propID ) {
			return config_data[i].paramValue;
		}
	}
	return "?";
}

char* getTexStringForConfigValue(char* pName, char* moduleName) {
    int i;
    char* str = (char*)malloc(128); bzero(str, 128);
    for(i=0; i < config_data_length; i++) {
        if ( strcmp(config_data[i].paramName, pName) == 0 &&  strcmp(config_data[i].moduleName, moduleName) == 0 ) {
            sprintf(str, "%s & %s", str, config_data[i].paramValue);
        }
    }
    return str;
}

struct filtervalue {
	int size; // the first value will keep how many filtervals there are
	char value[256];
};

struct filtervalue* getFilterValues(char* pName, int propID) {
	struct filtervalue* fv = (struct filtervalue*)malloc(6 * sizeof(struct filtervalue));
	int i=0, j=0;
	for(i=0; i < 6; i++) {
		bzero(fv[i].value, 256);
	}
	
	for(i=0; i < config_data_length; i++) {
		if ( strcmp(config_data[i].paramName, pName) == 0 && propID == config_data[i].propID ) {
			strcpy(fv[j].value, config_data[i].paramValue);
			j++; 
		}
	}
	fv[0].size = j;
	return fv;
}

struct filtervalue* getFilterMountedValues(char* pName) {
	struct filtervalue* fv = (struct filtervalue*)malloc(6 * sizeof(struct filtervalue));
	int i=0, j=0;
	for(i=0; i < 6; i++) {
		bzero(fv[i].value, 256);
	}
	
	for(i=0; i < config_data_length; i++) {
		if ( strcmp(config_data[i].paramName, pName) == 0 ) {
			strcpy(fv[j].value, config_data[i].paramValue);
			j++; 
		}
	}
	fv[0].size = j;
	return fv;
}

void readSessionData() {
	int i, k, flag;
	char sql[1024];
	
	sprintf(sql, "select sessionID, sessionUser, sessionHost, sessionDate, version, runComment from Session where sessionID=%d;", sessionID);

	MYSQL_STMT *stmt;
	MYSQL_BIND bind[6];
	my_bool error[6];
	
	struct session sbuffer;

	//fprintf(stderr , "forming query..");
	if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
		fprintf(stderr,"error in mysql_stmt_init: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	flag = mysql_stmt_prepare(stmt, sql, strlen(sql));
	if(flag!=0) {
		fprintf(stderr,"error in mysql_stmt_prepare: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	memset(bind, 0, sizeof(bind));

	i = 0;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(sbuffer.sessionID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(sbuffer.sessionUser);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(sbuffer.sessionHost);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(sbuffer.sessionDate);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(sbuffer.version);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(sbuffer.runComment);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];

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
			memcpy(&(session_data), &(sbuffer), sizeof(struct session));
			i++;
		}
	}
	
	mysql_stmt_close(stmt);
	//fprintf(stderr,"done\n");

	/*printf("%d %s %s %s %s %s\n",
		session_data.sessionID,
		session_data.sessionUser,
		session_data.sessionHost,
		session_data.sessionDate,
		session_data.version,
		session_data.runComment);*/
}

void readPropData() {
	int i, k, flag;
	char sql[1024];
	
	sprintf(sql, "select Proposal.propID as propID, propName, propConf, t3.Priority as priority, coalesce(userRegions, 0) as nUserRegions from Proposal, (select t2.propID, Priority, userRegions  from (select count(*) as userRegions, nonPropID as propID from Config where Session_sessionID=%d and paramName='userRegion' group by propID) t1 RIGHT OUTER JOIN (select paramValue as Priority, nonPropID as propID from Config where Session_sessionID=%d and paramName='RelativeProposalPriority' group by propID ) t2 ON t1.propID=t2.propID) t3 where Proposal.propID=t3.propID;", sessionID, sessionID);

	MYSQL_STMT *stmt;
	MYSQL_BIND bind[5];
	my_bool error[5];
	
	struct proposal pbuffer;

	//fprintf(stderr , "forming query..");
	if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
		fprintf(stderr,"error in mysql_stmt_init: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	flag = mysql_stmt_prepare(stmt, sql, strlen(sql));
	if(flag!=0) {
		fprintf(stderr,"error in mysql_stmt_prepare: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	memset(bind, 0, sizeof(bind));

	i = 0;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(pbuffer.propID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(pbuffer.propName);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(pbuffer.propConf);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(pbuffer.priority);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(pbuffer.nUserRegions);
	bind[i].error = &error[i];

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
	proposal_list_length = mysql_stmt_num_rows(stmt);
	//fprintf(stderr,"reading %d proposals..", proposal_list_length);

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
			memcpy(&(proposal_list[i]), &(pbuffer), sizeof(struct proposal));
			i++;
		}
	}
	
	mysql_stmt_close(stmt);
	//fprintf(stderr,"done\n");

	for(i=0; i < proposal_list_length; i++) {
		char newName[100];
		bzero(newName, 100);

        int x;
        int index = -1;
        for(x=0; x < strlen(proposal_list[i].propConf); x++) {
            if ( proposal_list[i].propConf[x] == '/') {
                index = x;
            }
        }
        
		strncpy(newName, proposal_list[i].propConf + index + 1, strlen(proposal_list[i].propConf) - index);
		strcpy(proposal_list[i].propConf, newName);
       
	bzero(proposal_list[i].lookahead, 256);
	strcpy(proposal_list[i].lookahead, "False"); 
        for(x=0; x < config_data_length; x++) {
            if ( config_data[x].propID == proposal_list[i].propID && strcmp(config_data[x].paramName, "UseLookAhead") == 0 && strcmp(config_data[x].paramValue, "True") == 0){
                strcpy(proposal_list[i].lookahead, "True");
            }
        }
        
	}
	/*for(i=0; i < proposal_list_length; i++) {
		printf("%d %s %s %lf %d\n",
			proposal_list[i].propID,
			proposal_list[i].propName,
			proposal_list[i].propConf,
			proposal_list[i].priority,
			proposal_list[i].nUserRegions);
	}*/
}

void readObservationDataField(char* sql) {
	int i, k, flag;

	MYSQL_STMT *stmt;
	MYSQL_BIND bind[1];
	my_bool error[1];
	observation_datafield_length = 0;
	
	double obuffer;

	//fprintf(stderr , "forming query..");
	if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
		fprintf(stderr,"error in mysql_stmt_init: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	flag = mysql_stmt_prepare(stmt, sql, strlen(sql));
	if(flag!=0) {
		fprintf(stderr,"error in mysql_stmt_prepare: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	memset(bind, 0, sizeof(bind));

	i = 0;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(obuffer);
	bind[i].error = &error[i];

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
	observation_datafield_length = mysql_stmt_num_rows(stmt);
	//fprintf(stderr,"reading %d observation data field..", observation_datafield_length);

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
			observation_datafield[i] = obuffer;
			i++;
		}
	}
	
	mysql_stmt_close(stmt);
	//fprintf(stderr,"done\n");
}

void readFilterDataField(char* sql) {
	int i, k, flag;

	MYSQL_STMT *stmt;
	MYSQL_BIND bind[2];
	my_bool error[2];
	filter_datafield_length = 0;
	
	struct field_query_data fbuffer;

	//fprintf(stderr , "forming query..");
	if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
		fprintf(stderr,"error in mysql_stmt_init: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	flag = mysql_stmt_prepare(stmt, sql, strlen(sql));
	if(flag!=0) {
		fprintf(stderr,"error in mysql_stmt_prepare: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	memset(bind, 0, sizeof(bind));

	i = 0;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(fbuffer.filter);
	bind[i].buffer_length = 16;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(fbuffer.count);
	bind[i].error = &error[i];

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
	filter_datafield_length = mysql_stmt_num_rows(stmt);
	//fprintf(stderr,"reading %d field data field..", filter_datafield_length);

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
			memcpy(&(filter_datafield[i]), &(fbuffer), sizeof(struct field_query_data));
			i++;
		}
	}
	
	mysql_stmt_close(stmt);
	//fprintf(stderr,"done\n");
}

void readFieldsData() {
	int i, k, flag;
	char sql[1024];
	
	sprintf(sql, "select fieldID, fieldFov, fieldRA, fieldDec, fieldGL, fieldGB, fieldEL, fieldEB from Field");

	MYSQL_STMT *stmt;
	MYSQL_BIND bind[8];
	my_bool error[8];
	
	struct field fbuffer;

	//fprintf(stderr , "forming query..");
	if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
		fprintf(stderr,"error in mysql_stmt_init: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	flag = mysql_stmt_prepare(stmt, sql, strlen(sql));
	if(flag!=0) {
		fprintf(stderr,"error in mysql_stmt_prepare: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	memset(bind, 0, sizeof(bind));

	i = 0;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(fbuffer.fieldID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(fbuffer.fieldFov);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(fbuffer.fieldRA);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(fbuffer.fieldDec);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(fbuffer.fieldGL);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(fbuffer.fieldGB);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(fbuffer.fieldEL);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(fbuffer.fieldEB);
	bind[i].error = &error[i];

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
	field_data_length  = mysql_stmt_num_rows(stmt);
	//fprintf(stderr,"reading %d field_data..", field_data_length );

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
			memcpy(&(field_data[i]), &(fbuffer), sizeof(struct field));
			i++;
		}
	}
	
	mysql_stmt_close(stmt);
	//fprintf(stderr,"done\n");

	/*for(i=0; i < field_data_length; i++) {
		printf("%d %lf %lf %lf %lf %lf %lf %lf\n",
			field_data[i].fieldID,
			field_data[i].fieldFov,
			field_data[i].fieldRA,
			field_data[i].fieldDec,
			field_data[i].fieldGL,
			field_data[i].fieldGB,
			field_data[i].fieldEL,
			field_data[i].fieldEB);
	}*/
}
