// get pointers to data sorted by field
void getFieldData(int *numfields, int *start, int *len) {
  int lastfield, i, ii, sum;

  // reorder observations by field number
  qsort(obs, numobs, sizeof(observation), compareField);
  
  // get field pointers
  lastfield = -10;
  ii = 0;
  for(i=0; i<numobs; i++) {
    if(obs[i].field != lastfield) {
      lastfield = obs[i].field;
      start[ii] = i;
      ii++;
    }
  }
  start[ii] = i;

  sum = 0;
  for(i=0; i<ii; i++) {
    len[i] = start[i+1]-start[i];
    sum += len[i];
  }

  *numfields = ii;

  printf("number of individual fields: %d numobs: %d\n", ii, numobs);
  if(sum != numobs) {
    fprintf(stderr,"Error: getFieldData: sum of len: %d vs numobs: %d\n", sum, numobs);
    exit(1);
  }
}
