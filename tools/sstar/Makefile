UNAME := $(shell uname -s)

ifeq ($(UNAME), Linux)
	MYSQL_CONFIG_LIBS = `mysql_config --libs`
	MYSQL_CONFIG_CFLG = `mysql_config --cflags`
	CFLAGS = -g -Iinclude ${MYSQL_CONFIG_CFLG}
	LIBS = -Llib -largtable2 ${MYSQL_CONFIG_LIBS} -lcpgplot -lpgplot -lX11 -lpng -lsla -lefence
	GCC = gcc
	G77 = g77
endif
ifeq ($(UNAME), Darwin)
	MYSQL_CONFIG_LIBS = `/opt/local/lib/mysql5/bin/mysql_config --libs`
	MYSQL_CONFIG_CFLG = `/opt/local/lib/mysql5/bin/mysql_config --cflags`
	CFLAGS = -g -Iinclude ${MYSQL_CONFIG_CFLG}
	LIBS = -largtable2 ${MYSQL_CONFIG_LIBS} -lcpgplot -lpgplot -lX11 -lpng -lsla -lefence
	GCC = gcc
	G77 = gcc
endif

SRCDIR = src
SOURCE =  ${SRCDIR}/*.c
LDFLAGS = -g
BINDIR = bin
SCRDIR = script
RM = rm -f

checker: ${SOURCE}
	${GCC} ${CFLAGS} -c ${SRCDIR}/checker.c -o ${BINDIR}/checker.o 
	${GCC} ${CFLAGS} -c ${SRCDIR}/maketex.c -o ${BINDIR}/maketex.o
	${GCC} ${CFLAGS} -c ${SRCDIR}/tables_visit.c -o ${BINDIR}/tables_visit.o
	${GCC} ${CFLAGS} -c ${SRCDIR}/tables_coadded.c -o ${BINDIR}/tables_coadded.o
	${GCC} ${CFLAGS} -c ${SRCDIR}/website_home.c -o ${BINDIR}/website_home.o
	${GCC} ${CFLAGS} -c ${SRCDIR}/website_design.c -o ${BINDIR}/website_design.o
	${GCC} ${CFLAGS} -c ${SRCDIR}/website_stretch.c -o ${BINDIR}/website_stretch.o
	${G77} ${LDFLAGS} -o ${SCRDIR}/maketex ${BINDIR}/maketex.o ${LIBS}
	${G77} ${LDFLAGS} -o ${SCRDIR}/tables_visit ${BINDIR}/tables_visit.o ${LIBS}
	${G77} ${LDFLAGS} -o ${SCRDIR}/tables_coadded ${BINDIR}/tables_coadded.o ${LIBS}
	${G77} ${LDFLAGS} -o ${SCRDIR}/checker ${BINDIR}/checker.o  ${LIBS}
	${GCC} ${LDFLAGS} -o ${SCRDIR}/website_home ${BINDIR}/website_home.o
	${GCC} ${LDFLAGS} -o ${SCRDIR}/website_design ${BINDIR}/website_design.o
	${GCC} ${LDFLAGS} -o ${SCRDIR}/website_stretch ${BINDIR}/website_stretch.o

clean: 
	${RM} ${SCRDIR}/maketex
	${RM} ${SCRDIR}/checker
	${RM} ${SCRDIR}/website_home
	${RM} ${SCRDIR}/website_design
	${RM} ${SCRDIR}/website_stretch
	${RM} ${SCRDIR}/tables_visit
	${RM} ${SCRDIR}/tables_coadded
	${RM} ${BINDIR}/*.o
	${RM} ${SRCDIR}/*~
	${RM} ${SCRDIR}/*~
