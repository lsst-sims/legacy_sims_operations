SERVICES="mysqld"

check_opsim_run_dir() {

    [ ! -w ${OPSIM_RUN_DIR} ] &&
    {
        echo "ERROR: Unable to start OpSim"
        echo "ERROR: Write access required to OPSIM_RUN_DIR (${OPSIM_RUN_DIR})"
        exit 1
    }

    echo "INFO: OpSim execution directory : ${OPSIM_RUN_DIR}"
}
