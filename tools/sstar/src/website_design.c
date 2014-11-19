#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <string.h>
#include <sys/utsname.h>

int HTMLCHARS = 20000;
struct utsname host;

int main(int argc, char* argv[]) {
  if ( argc == 3 ) {
    char* htmlString = (char*)malloc(HTMLCHARS);
    bzero(htmlString, HTMLCHARS);
    htmlString = strcat(htmlString, "<html>\n<title>");
    htmlString = strcat(htmlString, "OSTAR</title>\n");

    htmlString = strcat(htmlString, "<body><h1>");
    uname(&host);
    char* headerString = (char*)malloc(HTMLCHARS);
    sprintf(headerString, "Analysis & Reporting for %s.%d", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</h1>\n");
    htmlString = strcat(htmlString, "<h1>Design Comparison</h1>\n");
    
    sprintf(headerString, "%s_%d_sstar.pdf", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<h2>Standard Report</h2>\n");
    htmlString = strcat(htmlString, "<ul><li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a></li>");

    htmlString = strcat(htmlString, "</ul>\n");    
    htmlString = strcat(htmlString, "<br>\n<h2>Selected Figures & Data Files</h2>\n");
    htmlString = strcat(htmlString, "<ul>");

    sprintf(headerString, "%s_%d_output.sql.gz", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; SQL file of fields from the ObsHistory Table</li>\n");

    sprintf(headerString, "%s_%d_output.dat.gz", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Flat DAT file of fields from the ObsHistory Table</li>\n");

    sprintf(headerString, "%s_%d_hourglass.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Full survey Filter Map</li>\n");

    sprintf(headerString, "%s_%d_SixVisits-Num.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Aitoff projection of the acquired number of visits over the entire survey by filter</li>\n");

    sprintf(headerString, "%s_%d_SixVisits.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Aitoff projection of the ratio of the acquired number of visits to the SRD number of visits over the entire survey by filter</li>\n");

    sprintf(headerString, "%s_%d_median5sigma.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Aitoff map of the median 5 sigma limiting magnitude of each stack of acquired fields by filter</li>\n");

    sprintf(headerString, "%s_%d_coadded5sigma.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Aitoff map of the coadded 5 sigma limiting magnitude for each stack of acquired fields by filter</li>\n");

    sprintf(headerString, "%s_%d_medianskyb.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Aitoff map of the median sky brightness of each stack of acquired fields by filter</li>\n");

    sprintf(headerString, "%s_%d_medianseeing.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Aitoff map of the median seeing of each stack of acquired fields by filter</li>\n");

    sprintf(headerString, "%s_%d_medianairmass.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Aitoff map of the median airmass of each stack of acquired fields by filter</li>\n");

    sprintf(headerString, "%s_%d_maxairmass.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Aitoff map of maximum airmass for each stack of acquired fields by filter</li>\n");

    sprintf(headerString, "%s_%d_slews.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Logarithmic distribution of observed fields with slew time and slew distance</li>\n");
    
    sprintf(headerString, "%s_%d_revisit_griz.png", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Sky coverage of NEO (~30 minute) pairs</li>\n");

    /*sprintf(headerString, "%s_%d_timesummary.txt", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Summary Time Statistics</li>\n");*/

    sprintf(headerString, "%s_%d_summaryreport.txt", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Slew Activitiy Statitics and Survey Completeness by Proposal</li>\n");
    
    /*sprintf(headerString, "%s_%d_timereport.txt", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, "<li><a href='");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</a>&nbsp; Statistics on Visits, Intervisit (slew) and Seeing per filter</li>\n");*/

    htmlString = strcat(htmlString, "</ul>\n");
    htmlString = strcat(htmlString, "<h2>All Files</h2>\n");
    htmlString = strcat(htmlString, "<ul><li><a href='.");
    sprintf(headerString, "'>%s.%d</a></li>\n<ul>\n", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</body>\n</html>\n");
    printf("%s\n", htmlString);
  } else {
    printf("Usage: ./website_design <host> <sessionid>\n");
  }
  return 0;
}

