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
    htmlString = strcat(htmlString, "<html><title>");
/*    htmlString = strcat(htmlString, "Operations Simulator Tools for Analysis & Reporting</title>"); */
    htmlString = strcat(htmlString, "OSTAR</title>\n");
    htmlString = strcat(htmlString, "<body>\n<h1>");

    uname(&host);
    char* headerString = (char*)malloc(HTMLCHARS);

    sprintf(headerString, "Analysis & Reporting for %s.%d", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "</h1>\n");
    
    htmlString = strcat(htmlString, "<h2>Comparison to SRD Design Specs</h2>\n");

    htmlString = strcat(htmlString, "<ul><li><a href='");
    sprintf(headerString, "design/%s_%d_design.html", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, "Design Output</a></li></ul>\n");


    htmlString = strcat(htmlString, "<br>\n<h2>Comparison to SRD Stretch Specs</h2>\n");
    htmlString = strcat(htmlString, "<ul><li><a href='");
    sprintf(headerString, "stretch/%s_%d_stretch.html", argv[1], atoi(argv[2]));
    htmlString = strcat(htmlString, headerString);
    htmlString = strcat(htmlString, "'>");
    htmlString = strcat(htmlString, "Stretch Output</a></li></ul>\n");

    htmlString = strcat(htmlString, "</body>\n</html>");
    printf("%s\n", htmlString);
  } else {
    printf("Usage: ./website_home <host> <sessionid>\n");
  }
  return 0;
}

