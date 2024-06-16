#!/usr/bin/bash

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"

ROOT="$(readlink -f "${SCRIPT_PATH}/../../../../..")"

. ${ROOT}/tests/lib.sh

. ${ROOT}/src/initscripts/system/functions

# read the date in
readhash "CONFIG" "${SCRIPT_PATH}/data/1"

# test if we read the correct data
test_that_key_in_arry_has_value "CONFIG" "RED_DHCP_HOSTNAME" "ipfire"
test_that_key_in_arry_has_value "CONFIG" "BLUE_MACADDR" "bc:30:7d:58:6b:e3"

test_that_output_is "${SCRIPT_PATH}/data/1_output_stdout" "1" readhash "CONFIG" "${SCRIPT_PATH}/data/1"
test_that_output_is "${SCRIPT_PATH}/data/1_output_stderr" "2" readhash "CONFIG" "${SCRIPT_PATH}/data/1"
 

