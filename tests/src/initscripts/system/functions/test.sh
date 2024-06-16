#!/usr/bin/bash

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"

ROOT="$(readlink -f "${SCRIPT_PATH}/../../../../..")"

. ${ROOT}/tests/lib.sh

. ${ROOT}/src/initscripts/system/functions

# read the date in
readhash "CONFIG" "${SCRIPT_PATH}/data/1"

# test if we read the correct data
test_value_in_array "CONFIG" "RED_DHCP_HOSTNAME" "ipfire"
test_value_in_array "CONFIG" "BLUE_MACADDR" "bc:30:7d:58:6b:e3"
