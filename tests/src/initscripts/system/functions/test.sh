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

# Test that comments are skipped
# apparently the way we read the file strips the whitespace, so the key does not contain any whitespace either
test_that_array_doesnt_have_key "CONFIG" "# Another Comment"
test_that_array_doesnt_have_key "CONFIG" "# Comment for testing"
test_that_array_doesnt_have_key "CONFIG" "# Comment for testing Comments with spaces before"

test_that_output_is "${SCRIPT_PATH}/data/1_output_stdout" "1" readhash "CONFIG" "${SCRIPT_PATH}/data/1"
test_that_output_is "${SCRIPT_PATH}/data/1_output_stderr" "2" readhash "CONFIG" "${SCRIPT_PATH}/data/1"
