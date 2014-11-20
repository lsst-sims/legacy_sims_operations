/* ------------------------------------------------------------------------
 * Function: comp_statistics
 * Purpose : Compute the average and standard deviation of an array of
 *           integers.
 * Input   : arr      - The array.
 *           n        - Its size.
 * Output  : average  - The average.
 *           std_dev  - The standard deviation.
 * 			 median   - Median
 * 			 outliers - Outliers > 3sigma
 * 			 inliers  - Inliers < 3sigma  
 * Returns : Nothing.
 ------------------------------------------------------------------------ */

void comp_statistics (double *arr, int n, double *average, double *std_dev, double* median, int* outliers, int* inliers)
{
	double sum = 0.0;           /* The sum of all elements so far. */
	double sum_sqrs = 0.0;      /* The sum of their squares. */
	double variance = 0.0;
	int i, j;
	*outliers = 0;
	*inliers = 0;

	*average = 0.0;
	*std_dev = 0.0;
	*median = 0.0;
	
	for (i = 0; i < n; i++)
	{
		sum += arr[i];
		sum_sqrs += arr[i]*arr[i];
	}
	
	/* Compute the average and variance, using the equality: Var(X) = E(X^2) - E(X)*E(X) */
	*average = (double)sum / (double)n;
	
	variance = (double)sum_sqrs / (double)n - (*average)*(*average);
	
	/* Compute the standard deviation. */
	*std_dev = sqrt(variance);

	/* Not required to sort because we do this in sql */
	/* Sorting is taking a lot of time */
	/*double temp;
	for(i = n-1; i>=0; i--) {
		for(j=1; j<=i; j++) {
			if ( arr[j-1] > arr[j]) {
				temp = arr[j-1];
				arr[j-1] = arr[j];
				arr[j] = temp;
			}
		}
	}*/
	if ( n != 0 ) {
		if  ( n % 2 == 0 ) {
			*median = (arr[(n/2)-1] + arr[n/2])/2.0;
		} else {
			*median = arr[n/2];
		}
	}

	double out_value = *average + (3 * (*std_dev));
	double in_value  = *average - (3 * (*std_dev));

	for (i=0; i < n; i++) {
		if ( arr[i] > out_value ) 
			(*outliers)++;
		if ( arr[i] < in_value ) 
			(*inliers)++;
	}
	return;
}
