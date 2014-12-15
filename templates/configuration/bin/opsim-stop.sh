#!/bin/sh

OPSIM_RUN_DIR={{OPSIM_RUN_DIR}}
. ${OPSIM_RUN_DIR}/bin/env.sh

check_opsim_run_dir

services_rev=`echo ${SERVICES} | tr ' ' '\n' | tac`
for service in $services_rev; do
    ${OPSIM_RUN_DIR}/etc/init.d/$service stop
done
