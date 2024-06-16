#!/usr/bin/bash

# Get the path of this file.
# This ist rather complex as we do not want the calling script file
# That why we use BASH_SOURCE[0]
LIB_DIR="$(readlink -f "${BASH_SOURCE[0]}")"
# In LIB_DIR is currently saved the path to this file you are currently reading
# but we need the directory where it is located so:
LIB_DIR="$(dirname "${LIB_DIR}")"


. ${LIB_DIR}/lib_color.sh

test_command() {

	if ! "$@" ; then
		echo -e "${CLR_RED_BG} Test failed: ${*} ${CLR_RESET}"
		return 1
	else
		echo -e "${CLR_GREEN_BG} Test succeded: ${*} ${CLR_RESET}"
		return 0
	fi
}

var_has_value() {
	[[ "${!1}" == "${2}" ]]
}
