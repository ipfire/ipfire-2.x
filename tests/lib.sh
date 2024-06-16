#!/usr/bin/bash

# Get the path of this file.
# This ist rather complex as we do not want the calling script file
# That why we use BASH_SOURCE[0]
LIB_DIR="$(readlink -f "${BASH_SOURCE[0]}")"
# In LIB_DIR is currently saved the path to this file you are currently reading
# but we need the directory where it is located so:
LIB_DIR="$(dirname "${LIB_DIR}")"


. ${LIB_DIR}/lib_color.sh

log_test_failed(){
	echo -e "${CLR_RED_R}FAILED:${CLR_RESET} ${*}"
}

log_test_succeded(){
	echo -e "${CLR_GREEN_R}PASSED:${CLR_RESET} ${*}"
}

test_command() {

	if ! "$@" ; then
		log_test_failed "${*}"
		return 1
	else
		log_test_succeded "${*}"
		return 0
	fi
}

var_has_value() {
	[[ "${!1}" == "${2}" ]]
}

test_that_array_is_defined() {
	local arrayname="${1}"

	# `declare -p` print out how the variable with the name $arrayname was declared
	# If the array was not declared as indexed or associative array we fail. We cannot check for a value in an array if 
	# we were not given array.
	if [[ ! "$(declare  -p "${arrayname}")" =~ "declare -a" && ! "$(declare  -p "${arrayname}")" =~ "declare -A" ]]; then
		log_test_failed "The array '${1}' does not exists. The variable is not set."
		return 1
	else
		log_test_succeded "The array '${1}' is defined."
		return 0
	fi
}

test_value_in_array() {
	local -n array="${1}"
	local arrayname="${1}"
	local key="${2}"
	local value="${3}"

	test_that_array_is_defined "${arrayname}"  || return 1

	# If key is not defined we return _
	# If the key is defined we return nothing
	# See also https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
	if [[ "${array["${key}"]+_}" == ""  ]]; then
		log_test_failed "The array does not contain the key '${key}', valid keys are: ${!array[*]}"
		return 1
	fi

	if [[ "${array[${key}]}" == "${value}" ]] ; then
		log_test_succeded "The array '${1}' contains the value '${value}' under the key '${key}'"
		return 0
	else
		log_test_failed "The array '${1}' contains the value '${array[${key}]}' under the key '${key} and not '${value}'"
		return 1
	fi
}

test_that_output_is(){
	local reference_output_file="${1}"
	local file_descriptor="${2}"
	shift
	shift

	local command="$@"

	local temp="$(mktemp)"

	case "${file_descriptor}" in
		"stdout"|"1")
			$command 1> "${temp}" 2>/dev/null
			;;
		"stderr"|"2")
			$command 2> "${temp}" 1>/dev/null
			;;
	esac

	if diff -u "${temp}" "${reference_output_file}" &> /dev/null; then
		log_test_succeded "The output of command '${command}' on file descriptor '${file_descriptor}' is equal to the reference output."
	else
		log_test_failed "The output of command '${command}' on file descriptor '${file_descriptor}' is unequal to the reference output."
		diff -u --color "${reference_output_file}" "${temp}"
	fi

	rm "${temp}"
}
