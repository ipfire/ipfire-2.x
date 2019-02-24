#!/bin/bash
# This scripts lists binaries that have missing libraries.
# Arguments are paths to search in

main() {
	local path
	for path in $@; do
		local file
		for file in $(find "${path}" -type f); do
			if ldd "${file}" 2>/dev/null | grep -q "not found"; then
				echo "${file}"
				ldd "${file}"
			fi
		done
	done
}

main "$@" || exit $?
