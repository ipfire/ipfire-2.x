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

test_value_in_array() {
	local -n array="${1}"
	local arrayname="${1}"
	local key="${2}"
	local value="${3}"

	# `declare -p` print out how the variable with the name $arrayname was declared
	# If the array was not declared as indexed or associative array we fail. We cannot check for a value in an array if 
	# we were not given array.
	if [[ ! "$(declare  -p "${arrayname}")" =~ "declare -a" && ! "$(declare  -p "${arrayname}")" =~ "declare -A" ]]; then
		echo -e "${CLR_RED_BG}Test failed: The array '${1}' does not exists. The variable is not set.${CLR_RESET}'"
		return 1
	fi

	if [[ "${array[${key}]}" == "${value}" ]] ; then
		echo -e "${CLR_GREEN_BG}Test succeded: The array '${1}' contains the value '${value}' under the key '${key}' ${CLR_RESET}"
		return 0
	else
		echo -e "${CLR_RED_BG}Test failed: The array '${1}' contains the value '${array[${key}]}' under the key '${key} and not '${value}' ${CLR_RESET}"
		return 1
	fi
}
