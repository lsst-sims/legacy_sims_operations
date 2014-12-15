#!/bin/sh

OPSIM_RUN_DIR={{OPSIM_RUN_DIR}}
. ${OPSIM_RUN_DIR}/bin/env.sh

check_opsim_run_dir

for service in ${SERVICES}; do
    ${OPSIM_RUN_DIR}/etc/init.d/$service start
done
