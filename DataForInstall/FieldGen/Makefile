SLALIB = /data1/simulator/sw/src/slalib_c
INCLUDE = -I${SLALIB}
CFLAGS = ${INCLUDE}
LIB = -L${SLALIB}

AddGalEcl : AddGalEcl.o
	gcc -o AddGalEcl AddGalEcl.o ${LIB} -lsla -lm
