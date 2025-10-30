#!/bin/bash
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2025  IPFire Team  <info@ipfire.org>                     #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

NAME="IPFire"							# Software name
SNAME="ipfire"							# Short name
# If you update the version don't forget to update backupiso and add it to core update
VERSION="2.29"							# Version number
CORE="199"							# Core Level (Filename)
SLOGAN="www.ipfire.org"						# Software slogan
CONFIG_ROOT=/var/ipfire						# Configuration rootdir

# Information from Git
GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"			# Git Branch
GIT_TAG="$(git tag | tail -1)"					# Git Tag
GIT_LASTCOMMIT="$(git rev-parse --verify HEAD)"			# Last commit

TOOLCHAINVER="20250814"

KVER_SUFFIX="-${SNAME}"

# Kernel Version
KVER="$(grep --max-count=1 VER lfs/linux | awk '{ print $3 }')"
KVER="${KVER/-rc/.0-rc}${KVER_SUFFIX}"

###############################################################################
#
# Beautifying variables & presentation & input output interface
#
###############################################################################

# All supported architectures
ARCHES=(
	aarch64
	riscv64
	x86_64
)

HOST_ARCH="${HOSTTYPE}"
HOST_KERNEL="$(uname -r)"
LC_ALL=POSIX
PS1='\u:\w$ '

HAS_TIME_NAMESPACE="true"

# Disable time namespaces for older kernels
case "${HOST_KERNEL}" in
	4.*|5.[12345].*)
		HAS_TIME_NAMESPACE="false"
		;;
esac

# Are we reading from/writing to a terminal?
is_terminal() {
	[ -t 0 ] && [ -t 1 ] && [ -t 2 ]
}

# Define color for messages
if is_terminal; then
	BOLD="$(tput bold)"
	RED="$(tput setaf 1)"
	GREEN="$(tput setaf 2)"
	YELLOW="$(tput setaf 3)"
	CYAN="$(tput setaf 6)"
	NORMAL="$(tput sgr0)"
fi

# Sets or adjusts pretty formatting variables
resize_terminal() {
	# Find current screen size
	COLUMNS="$(tput cols)"

	# When using remote connections, such as a serial port, stty size returns 0
	if ! is_terminal || [ "${COLUMNS}" = "0" ]; then
		COLUMNS=80
	fi

	# Wipe any previous content before updating the counters
	if [ -n "${TIME_COL}" ]; then
		tput hpa "${TIME_COL}"
		tput el
	fi

	# The status column is always 8 characters wide
	STATUS_WIDTH=8

	# The time column is always 12 characters wide
	TIME_WIDTH=12

	# Where do the columns start?
	(( STATUS_COL = COLUMNS - STATUS_WIDTH ))
	(( TIME_COL   = STATUS_COL - TIME_WIDTH ))
}

# Initially setup terminal
resize_terminal

# Call resize_terminal when terminal is being resized
trap "resize_terminal" WINCH

# Writes a line to the log file
log() {
	local line="$@"

	# Fetch the current timestamp
	local t="$(date -u "+%b %e %T")"

	# Append the line to file
	if [ -w "${LOGFILE}" ]; then
		echo "${t}: ${line}" >> "${LOGFILE}"
	fi

	return 0
}

find_base() {
	local path

	# Figure out the absolute script path using readlink
	path="$(readlink -f "${0}" 2>&1)"

	# If that failed, try realpath
	if [ -z "${path}" ]; then
		path="$(realpath "${0}" 2>&1)"
	fi

	# If that failed, I am out of ideas
	if [ -z "${path}" ]; then
		echo "${0}: Could not determine BASEDIR" >&2
		return 1
	fi

	# Return the dirname
	dirname "${path}"
}

system_processors() {
	getconf _NPROCESSORS_ONLN 2>/dev/null || echo "1"
}

system_memory() {
	local key val unit

	while read -r key val unit; do
		case "${key}" in
			MemTotal:*)
				# Convert to MB
				echo "$(( ${val} / 1024 ))"
				break
				;;
		esac
	done < /proc/meminfo
}

format_runtime() {
	local seconds=${1}

	if [ ${seconds} -ge 3600 ]; then
		printf "%d:%02d:%02d\n" \
			"$(( seconds / 3600 ))" \
			"$(( seconds % 3600 / 60 ))" \
			"$(( seconds % 3600 % 60 ))"
	elif [ ${seconds} -ge 60 ]; then
		printf "%d:%02d\n" \
			"$(( seconds / 60 ))" \
			"$(( seconds % 60 ))"
	else
		printf "%d\n" "${seconds}"
	fi
}

print_line() {
	# Print the string all the way to the status column
	printf "%-${STATUS_COL}s" "$*"
}

print_headline() {
	printf "${BOLD}%s${NORMAL}\n" "$*"
}

print_package() {
	local name="${1}"
	shift

	local version="$(grep -E "^VER |^VER=|^VER	" $BASEDIR/lfs/${name} | awk '{ print $3 }')"
	local options="$@"

	local string="${name}"
	if [ -n "${version}" ] && [ "${version}" != "ipfire" ]; then
		string="${string} (${version})"
	fi

	# Add the options
	if [ -n "${options}" ]; then
		string="${string} ${options[@]}"
	fi

	# Print the string
	print_line "${string}"
}

print_runtime() {
	local runtime=$(format_runtime $@)

	# Move back the cursor to rewrite the runtime
	if is_terminal; then
		tput hpa "${TIME_COL}"
	fi

	printf "[ ${BOLD}%$(( TIME_WIDTH - 4 ))s${NORMAL} ]" "${runtime}"
}

print_status() {
	local status="${1}"
	local color

	case "${status}" in
		DONE)
			color="${BOLD}${GREEN}"
			;;
		FAIL)
			color="${BOLD}${RED}"
			;;
		SKIP)
			color="${BOLD}${CYAN}"
			;;
		WARN)
			color="${BOLD}${YELLOW}"
			;;
		*)
			color="${BOLD}"
			;;
	esac

	# Move to the start of the column
	if is_terminal; then
		tput hpa "${STATUS_COL}"
	fi

	printf "[ ${color}%$(( STATUS_WIDTH - 4 ))s${NORMAL} ]\n" "${status}"
}

print_build_summary() {
	local runtime="${1}"

	print_line "*** Build Finished"
	print_runtime "${runtime}"
	print_status DONE
}

# Launches a timer process as a co-process
launch_timer() {
	# Do nothing if the timer is already running
	if [ -n "${TIMER_PID}" ]; then
		return 0
	fi

	# Don't launch the timer when we are not on a terminal
	if ! is_terminal; then
		return 0
	fi

	# Launch the co-process
	coproc TIMER { "${0}" "__timer" "$$"; }

	# Register the signal handlers
	trap "__timer_event" SIGUSR1
	trap "terminate_timer" EXIT
}

# Terminates a previously launched timer
terminate_timer() {
	if [ -n "${TIMER_PID}" ]; then
		kill -TERM "${TIMER_PID}"
	fi
}

# The timer main loop
__timer() {
	local pid="${1}"

	# Send SIGUSR1 to the main process once a second
	# If the parent process has gone away, we will terminate.
	while sleep 1; do
		if ! kill -USR1 "${pid}" &>/dev/null; then
			break
		fi
	done

	return 0
}

# Called when the timer triggers
# This function does nothing, but is needed interrupt the wait call
__timer_event() {
	return 0
}

exiterror() {
	# Dump logfile
	if [ -n "${LOGFILE}" ] && [ -e "${LOGFILE}" ]; then
		echo # empty line

		local line
		while read -r line; do
			echo "    ${line}"
		done <<< "$(tail -n30 ${LOGFILE})"
	fi

	echo # empty line

	local line
	for line in "ERROR: $@" "    Check ${LOGFILE} for errors if applicable"; do
		print_line "${line}"
		print_status FAIL
	done

	exit 1
}

prepareenv() {
	local network="false"

	# Are we running the right shell?
	if [ -z "${BASH}" ]; then
		exiterror "BASH environment variable is not set.  You're probably running the wrong shell."
	fi

	if [ -z "${BASH_VERSION}" ]; then
		exiterror "Not running BASH shell."
	fi

	# Trap on emergency exit
	trap "exiterror 'Build process interrupted'" SIGINT SIGTERM SIGQUIT

	# Checking if running as root user
	if [ "${UID}" -ne 0 ]; then
		exiterror "root privileges required for building"
	fi

	local required_space

	# Parse arguments
	while [ $# -gt 0 ]; do
		case "${1}" in
			--required-space=*)
				required_space="${1#--required-space=}"
				;;

			--network)
				network="true"
				;;

			*)
				exiterror "Unknown argument: ${1}"
				;;
		esac
		shift
	done

	# Do we need to check the required space?
	if [ -n "${required_space}" ]; then
		local free_space free_blocks block_size
		local consumed_space path

		# Fetch free blocks
		read -r free_blocks block_size <<< "$(stat --file-system --format="%a %S" "${BASEDIR}")"

		# Calculate free space
		(( free_space = free_blocks * block_size / 1024 / 1024 ))

		# If we don't have the total space free, we need to check how much we have consumed already...
		if [ "${free_space}" -lt "${required_space}" ]; then
			# Add any consumed space
			while read -r consumed_space path; do
				(( free_space += consumed_space / 1024 / 1024 )) 
			done <<< "$(du --summarize --bytes "${BUILD_DIR}" "${IMAGES_DIR}" "${LOG_DIR}" 2>/dev/null)"
		fi

		# Check that we have the required space
		if [ "${free_space}" -lt "${required_space}" ]; then
			exiterror "Not enough temporary space available, need at least ${required_space}MiB, but only have ${free_space}MiB"
		fi
	fi

	# Set umask
	umask 022

	# Make some extra directories
	mkdir -p "${CCACHE_DIR}"
	mkdir -p "${IMAGES_DIR}"
	mkdir -p "${PACKAGES_DIR}"
	mkdir -p "${BUILD_DIR}/${TOOLS_DIR}"
	mkdir -p "${BUILD_DIR}/cache"
	mkdir -p "${BUILD_DIR}/dev"
	mkdir -p "${BUILD_DIR}/etc"
	mkdir -p "${BUILD_DIR}/proc"
	mkdir -p "${BUILD_DIR}/root"
	mkdir -p "${BUILD_DIR}/sys"
	mkdir -p "${BUILD_DIR}/tmp"
	mkdir -p "${BUILD_DIR}/usr/src"
	mkdir -p "${BUILD_DIR}/usr/src/cache"
	mkdir -p "${BUILD_DIR}/usr/src/ccache"
	mkdir -p "${BUILD_DIR}/usr/src/config"
	mkdir -p "${BUILD_DIR}/usr/src/doc"
	mkdir -p "${BUILD_DIR}/usr/src/html"
	mkdir -p "${BUILD_DIR}/usr/src/images"
	mkdir -p "${BUILD_DIR}/usr/src/langs"
	mkdir -p "${BUILD_DIR}/usr/src/lfs"
	mkdir -p "${BUILD_DIR}/usr/src/log"
	mkdir -p "${BUILD_DIR}/usr/src/src"

	# Make BUILD_DIR a mountpoint
	mount -o bind "${BUILD_DIR}" "${BUILD_DIR}"

	# Create a new, minimal /dev
	mount build_dev "${BUILD_DIR}/dev" \
		-t devtmpfs -o "nosuid,noexec,mode=0755,size=4m,nr_inodes=64k"

	# Mount a new /dev/pts
	mount build_dev_pts "${BUILD_DIR}/dev/pts" \
		-t devpts -o "nosuid,noexec,newinstance,ptmxmode=0666,mode=620"

	# Mount a new /dev/shm
	mount build_dev_shm "${BUILD_DIR}/dev/shm" \
		-t tmpfs -o "nosuid,nodev,strictatime,mode=1777,size=1024m"

	# Mount a new /tmp
	mount build_tmp "${BUILD_DIR}/tmp" \
		-t tmpfs -o "nosuid,nodev,strictatime,size=4G,nr_inodes=1M,mode=1777"

	# Create an empty /proc directory and make it a mountpoint
	mkdir -p "${BUILD_DIR}/proc"
	mount --bind "${BUILD_DIR}/proc" "${BUILD_DIR}/proc"

	# Make all sources and proc available under lfs build
	mount --bind     	/sys					"${BUILD_DIR}/sys"
	mount --bind -o ro	"${BASEDIR}/cache"		"${BUILD_DIR}/usr/src/cache"
	mount --bind -o ro	"${BASEDIR}/config"		"${BUILD_DIR}/usr/src/config"
	mount --bind -o ro	"${BASEDIR}/doc"		"${BUILD_DIR}/usr/src/doc"
	mount --bind -o ro	"${BASEDIR}/html"		"${BUILD_DIR}/usr/src/html"
	mount --bind -o ro	"${BASEDIR}/langs"		"${BUILD_DIR}/usr/src/langs"
	mount --bind -o ro	"${BASEDIR}/lfs"		"${BUILD_DIR}/usr/src/lfs"
	mount --bind -o ro	"${BASEDIR}/src"		"${BUILD_DIR}/usr/src/src"

	# Mount the log directory
	mount --bind "${LOG_DIR}"			"${BUILD_DIR}/usr/src/log"

	# Mount the ccache
	mount --bind "${CCACHE_DIR}"		"${BUILD_DIR}/usr/src/ccache"

	# Mount the images directory
	mount --bind "${IMAGES_DIR}"		"${BUILD_DIR}/usr/src/images"

	# Bind-mount files requires for networking if requested
	if [ "${network}" = "true" ]; then
		local file

		for file in /etc/resolv.conf /etc/hosts; do
			# Skip if the source files does not exist
			if [ ! -e "${file}" ]; then
				continue
			fi

			# Create the destination if it does not exist
			if [ ! -e "${BUILD_DIR}/${file}" ]; then
				touch "${BUILD_DIR}/${file}"
			fi

			# Mount the file read-only
			mount --bind -o ro "${file}" "${BUILD_DIR}/${file}"
		done
	fi

	# Configure the ccache
	export CCACHE_TEMPDIR="/tmp"
	export CCACHE_COMPILERCHECK="string:toolchain-${TOOLCHAINVER} ${BUILD_ARCH}"

	# Install the QEMU helper
	qemu_install_helper

	# Remove pre-install list of installed files in case user erase some files before rebuild
	rm -f "${BUILD_DIR}/usr/src/lsalr"

	# Prepare string for /etc/system-release.
	local system_release="${NAME} ${VERSION} (${BUILD_ARCH})"

	case "${GIT_BRANCH}" in
		core*|beta?|rc?)
			system_release="${system_release} - ${GIT_BRANCH}"
			;;
		*)
			system_release="${system_release} - core${CORE} Development Build: ${GIT_BRANCH}/${GIT_LASTCOMMIT:0:8}"
			;;
	esac

	# Append -dirty tag for local changes
	if [ "$(git status -s | wc -l)" != "0" ]; then
		system_release="${system_release}-dirty"
	fi

	# Export variable
	SYSTEM_RELEASE="${system_release}"

	# Decide on PAKFIRE_TREE
	case "${GIT_BRANCH}" in
		core*)
			PAKFIRE_TREE="stable"
			;;
		master)
			PAKFIRE_TREE="testing"
			;;
		*)
			PAKFIRE_TREE="unstable"
			;;
	esac

	# Setup ccache cache size
	execute --chroot ccache --max-size="${CCACHE_CACHE_SIZE}"
}

entershell() {
	echo "Entering to a shell inside the build environment, go out with exit"

	local PS1="ipfire build chroot (${BUILD_ARCH}) \u:\w\$ "

	# Run an interactive shell
	execute --chroot --interactive --network bash -i
}

lfsmakecommoncheck() {
	# Script present?
	if [ ! -f $BASEDIR/lfs/$1 ]; then
		exiterror "No such file or directory: $BASEDIR/$1"
	fi

	# Print package name and version
	print_package $@

	# Check if this package is supported by our architecture.
	# If no SUP_ARCH is found, we assume the package can be built for all.
	if grep "^SUP_ARCH" ${BASEDIR}/lfs/${1} >/dev/null; then
		# Check if package supports ${BUILD_ARCH} or all architectures.
		if ! grep -E "^SUP_ARCH.*${BUILD_ARCH}|^SUP_ARCH.*all" ${BASEDIR}/lfs/${1} >/dev/null; then
			print_runtime 0
			print_status SKIP
			return 1
		fi
	fi

	echo -ne "`date -u '+%b %e %T'`: Building $* " >> $LOGFILE

	return 0	# pass all!
}

execute() {
	local chroot="false"
	local command=()
	local interactive="false"
	local timer
	local network="false"

	# Collect environment variables
	local -A environ=(
		[PATH]="${TOOLS_DIR}/ccache/bin:${TOOLS_DIR}/sbin:${TOOLS_DIR}/bin:${PATH}"
		[HOME]="${HOME}"
		[PS1]="${PS1}"
		[TERM]="vt100"

		# Distro Information
		[NAME]="${NAME}"
		[SNAME]="${SNAME}"
		[VERSION]="${VERSION}"
		[CORE]="${CORE}"
		[SLOGAN]="${SLOGAN}"
		[SYSTEM_RELEASE]="${SYSTEM_RELEASE}"
		[PAKFIRE_TREE]="${PAKFIRE_TREE}"
		[CONFIG_ROOT]="${CONFIG_ROOT}"

		# Kernel Version
		[KVER]="${KVER}"
		[KVER_SUFFIX]="${KVER_SUFFIX}"

		# Compiler flags
		[CFLAGS]="${CFLAGS[@]}"
		[CXXFLAGS]="${CFLAGS[@]}"
		[RUSTFLAGS]="${RUSTFLAGS[@]}"

		# ccache
		[CCACHE_DIR]="${CCACHE_DIR}"
		[CCACHE_TEMPDIR]="${CCACHE_TEMPDIR}"
		[CCACHE_COMPILERCHECK]="${CCACHE_COMPILERCHECK}"

		# System Properties
		[SYSTEM_PROCESSORS]="${SYSTEM_PROCESSORS}"
		[SYSTEM_MEMORY]="${SYSTEM_MEMORY}"

		# Parallelism
		[DEFAULT_PARALLELISM]="${DEFAULT_PARALLELISM}"

		# Compression Options
		[XZ_OPT]="${XZ_OPT[*]}"
		[ZSTD_OPT]="${ZSTD_OPT[*]}"

		# Build Architecture
		[BUILD_ARCH]="${BUILD_ARCH}"
		[BUILD_PLATFORM]="${BUILD_PLATFORM}"

		# Targets
		[CROSSTARGET]="${CROSSTARGET}"
		[BUILDTARGET]="${BUILDTARGET}"

		# Paths
		[LFS_BASEDIR]="${BASEDIR}"
		[BUILD_DIR]="${BUILD_DIR}"
		[IMAGES_DIR]="${IMAGES_DIR}"
		[LOG_DIR]="${LOG_DIR}"
		[PACKAGES_DIR]="${PACKAGES_DIR}"
		[TOOLS_DIR]="${TOOLS_DIR}"
	)

	local unshare=()

	# Configure a new namespace
	if [ -n "${IN_NAMESPACE}" ]; then
		unshare+=(
			# Create a new cgroup namespace
			"--cgroup"

			# Create a new mount namespace
			"--mount"
			"--propagation=slave"

			# Create a new PID namespace and fork
			"--pid"
			"--fork"

			# Create a new UTS namespace
			"--uts"

			# Mount /proc so that the build environment does not see
			# any foreign processes.
			"--mount-proc=${BUILD_DIR}/proc"

			# If unshare is asked to terminate, terminate all child processes
			"--kill-child"
		)

		# Optionally set up a new time namespace
		if [ "${HAS_TIME_NAMESPACE}" = "true" ]; then
			unshare+=( "--time" )
		fi
	fi

	while [ $# -gt 0 ]; do
		case "${1}" in
			--chroot)
				chroot="true"

				# Update some variables
				environ+=(
					[PATH]="${TOOLS_DIR}/ccache/bin:/bin:/usr/bin:/sbin:/usr/sbin"
					[HOME]="/root"

					# Paths
					[LFS_BASEDIR]="/usr/src"
					[BUILD_DIR]="/"
					[IMAGES_DIR]="/usr/src/images"
					[LOG_DIR]="/usr/src/log"
					[PACKAGES_DIR]="/usr/src/images/packages"

					# Compiler Cache
					[CCACHE_DIR]="/usr/src/ccache"

					# Go Cache
					[GOCACHE]="/usr/src/ccache/go"
				)

				# Fake environment
				if [ -e "${BUILD_DIR}${TOOLS_DIR}/lib/libpakfire_preload.so" ]; then
					environ+=(
						[LD_PRELOAD]="${TOOLS_DIR}/lib/libpakfire_preload.so"

						# Fake kernel version, because some of the packages do not
						# compile with kernel 3.0 and later
						[UTS_RELEASE]="${KVER}"

						# Fake machine
						[UTS_MACHINE]="${BUILD_ARCH}"
					)
				fi
				;;

			# Make the toolchain available in PATH
			--enable-toolchain)
				environ+=(
					[PATH]="${environ[PATH]}:${TOOLS_DIR}/sbin:${TOOLS_DIR}/bin"
				)
				;;

			--interactive)
				interactive="true"

				# Use the actual value of $TERM
				environ+=(
					[TERM]="${TERM}"
				)
				;;

			--network)
				network="true"

				# Export the proxy configuration
				environ+=(
					[https_proxy]="${https_proxy}"
					[http_proxy]="${http_proxy}"
				)
				;;

			--timer=*)
				timer="${1#--timer=}"
				;;

			-*)
				echo "Unknown argument: ${1}" >&2
				return 2
				;;

			# Parse any custom environment variables
			*=*)
				environ["${1%=*}"]="${1#*=}"
				;;

			# The rest is the command
			*)
				command+=( "$@" )
				break
				;;
		esac
		shift
	done

	# Prepend any custom changes to PATH
	if [ -n "${CUSTOM_PATH}" ]; then
		environ[PATH]="${CUSTOM_PATH}:${environ[PATH]}"
	fi

	# Setup QEMU
	if qemu_is_required; then
		environ+=(
			[QEMU_TARGET_HELPER]="${QEMU_TARGET_HELPER}"

			# Enable QEMU strace
			#[QEMU_STRACE]="1"
		)

		case "${BUILD_ARCH}" in
			arm*)
				environ+=(
					[QEMU_CPU]="${QEMU_CPU:-cortex-a9}"
				)
				;;

			riscv64)
				environ+=(
					[QEMU_CPU]="${QEMU_CPU:-sifive-u54}"

					# Bug fix for QEMU locking up
					[G_SLICE]="always-malloc"
				)
				;;
		esac
	fi

	# Network
	if [ "${network}" = "false" ]; then
		unshare+=( "--net" )
	fi

	local execute=()
	local env

	# Create new namespaces
	if [ "${#unshare[@]}" -gt 0 ]; then
		execute+=(
			"unshare" "${unshare[@]}"
		)
	fi

	# Call a setup script in the new namespaces to perform
	# further set up, but before we change root.
	execute+=( "${BASEDIR}/tools/execute.sh" )

	# Run in chroot?
	if [ "${chroot}" = "true" ]; then
		execute+=( "chroot" "${BUILD_DIR}" )
	fi

	# Set PATH so that we can find the env binary
	local PATH="${environ[PATH]}:${PATH}"

	# Reset the environment
	execute+=(
		"env"

		# Clear the previous environment
		"--ignore-environment"

		# Change to the home directory
		--chdir="${environ[HOME]}"
	)

	# Export the environment
	for env in ${!environ[@]}; do
		execute+=( "${env}=${environ[${env}]}" )
	done

	# Append the command
	execute+=( "${command[@]}" )

	local pid

	# Return code
	local r=0

	# Store the start time
	local t="${SECONDS}"

	# Run the command in the background and pipe all output to the logfile
	case "${interactive}" in
		true)
			"${execute[@]}" || return $?
			;;

		false)
			# Launch the timer if needed
			if [ -n "${timer}" ]; then
				launch_timer
			fi

			# Dispatch the command to the background
			{
				"${execute[@]}" >> "${LOGFILE}" 2>&1 </dev/null
			} &

			# Store the PID
			pid="$!"

			# Wait for the process to complete
			while :; do
				wait "${pid}"

				# Store the return code
				r="$?"

				case "${r}" in
					# Code means that we have received SIGUSR1 from the timer
					138)
						# Call the timer callback
						if [ -n "${timer}" ]; then
							"${timer}"
						fi

						# Go back and wait
						continue
						;;

					# Ignore SIGWINCH
					156)
						continue
						;;
				esac

				break
			done

			# Call the timer callback at least once
			if [ -n "${timer}" ]; then
				"${timer}"
			fi
	esac

	return "${r}"
}

# Calls the makefile of a package
make_pkg() {
	local args=()
	local pkg

	local basedir="${BASEDIR}"

	while [ $# -gt 0 ]; do
		local arg="${1}"
		shift

		case "${arg}" in
			--*)
				case "${arg}" in
					--chroot)
						basedir="/usr/src"
						;;
				esac

				args+=( "${arg}" )
				;;

			*)
				pkg="${arg}"
				break
				;;
		esac
	done

	# Execute the make command in the environment
	execute "${args[@]}" make --directory="${basedir}/lfs" --file="${pkg}" "$@"
}

lfsmake1() {
	local pkg="${1}"
	shift

	# Run the common check
	lfsmakecommoncheck "${pkg}" "$@"
	[ $? == 1 ] && return 0

	# Download source outside of the toolchain
	if ! make_pkg --network "${pkg}" download "$@"; then
		exiterror "Downloading ${pkg}"
	fi

	if ! make_pkg --timer="update_runtime" "${pkg}" TOOLCHAIN=1 ROOT="${BUILD_DIR}" b2 install "$@"; then
		print_status FAIL

		exiterror "Building ${pkg}"
	fi

	print_status DONE
}

lfsmake2() {
	local args=()
	local pkg

	# Parse command line arguments
	while [ $# -gt 0 ]; do
		local arg="${1}"
		shift

		case "${arg}" in
			# Collect any arguments
			--*)
				args+=( "${arg}" )
				;;

			# Abort once we found the package
			*)
				pkg="${arg}"
				break
				;;
		esac
	done

	# Run the common check
	lfsmakecommoncheck "${pkg}" "$@"
	[ $? == 1 ] && return 0

	# Download source outside of the toolchain
	if ! make_pkg --network "${args[@]}" "${pkg}" download "$@"; then
		exiterror "Downloading ${pkg}"
	fi

	# Run install on the package
	if ! make_pkg --chroot --timer="update_runtime" \
			"${args[@]}" "${pkg}" b2 install "$@"; then
		print_status FAIL

		exiterror "Building ${pkg}"
	fi

	print_status DONE
}

ipfiredist() {
	local pkg="${1}"
	shift

	# Run the common check
	lfsmakecommoncheck "${pkg}" "$@"
	[ $? == 1 ] && return 0

	# Run dist on the package
	if ! make_pkg --chroot --timer="update_runtime" "${pkg}" dist "$@"; then
		print_status FAIL

		exiterror "Packaging ${pkg}"
	fi

	print_status DONE
}

update_runtime() {
	print_runtime "$(( SECONDS - t ))"
}

qemu_is_required() {
	local build_arch="${1}"

	if [ -z "${build_arch}" ]; then
		build_arch="${BUILD_ARCH}"
	fi

	case "${HOST_ARCH},${build_arch}" in
		x86_64,arm*|x86_64,aarch64|x86_64,riscv64|i?86,arm*|i?86,aarch64|i?86,x86_64)
			return 0
			;;
		*)
			return 1
			;;
	esac
}

qemu_install_helper() {
	# Do nothing, if qemu is not required
	if ! qemu_is_required; then
		return 0
	fi

	if [ ! -e /proc/sys/fs/binfmt_misc/status ]; then
		exiterror "binfmt_misc not mounted. QEMU_TARGET_HELPER not useable."
	fi

	if [ ! $(cat /proc/sys/fs/binfmt_misc/status) = 'enabled' ]; then
		exiterror "binfmt_misc not enabled. QEMU_TARGET_HELPER not useable."
	fi

	# Search for the helper binary
	local qemu_build_helper="$(qemu_find_build_helper_name "${BUILD_ARCH}")"

	# Try to find a suitable binary that we can install
	# to the build environment.
	local file
	for file in "${qemu_build_helper}" "${qemu_build_helper}-static"; do
		# file must exist and be executable.
		[ -x "${file}" ] || continue

		# Must be static.
		file_is_static "${file}" || continue

		local dirname="${BUILD_DIR}$(dirname "${file}")"
		mkdir -p "${dirname}"

		# Create the mountpoint
		touch "${BUILD_DIR}${file}"

		# Mount the helper
		if ! mount --bind -o ro "${file}" "${BUILD_DIR}${file}"; then
			exiterror "Could not mount ${file}"
		fi

		# Set
		QEMU_TARGET_HELPER="${file}"

		return 0
	done

	exiterror "Could not find a statically-linked QEMU emulator: ${qemu_build_helper}"
}

qemu_find_build_helper_name() {
	local build_arch="${1}"

	local magic
	case "${build_arch}" in
		aarch64)
			magic="7f454c460201010000000000000000000200b700"
			;;
		arm*)
			magic="7f454c4601010100000000000000000002002800"
			;;
		riscv64)
			magic="7f454c460201010000000000000000000200f300"
			;;
		x86_64)
			magic="7f454c4602010100000000000000000002003e00"
			;;
	esac

	[ -z "${magic}" ] && return 1

	local file
	for file in /proc/sys/fs/binfmt_misc/*; do
		# skip write only register entry
		[ $(basename "${file}") = "register" ] && continue
		# Search for the file with the correct magic value.
		grep -qE "^magic ${magic}$" "${file}" || continue

		local interpreter="$(grep "^interpreter" "${file}" | awk '{ print $2 }')"

		[ -n "${interpreter}" ] || continue
		[ "${interpreter:0:1}" = "/" ] || continue
		[ -x "${interpreter}" ] || continue

		echo "${interpreter}"
		return 0
	done

	return 1
}

file_is_static() {
	local file="${1}"

	file -L "${file}" 2>/dev/null | grep -q -e "statically linked" -e "static-pie linked"
}

update_language_list() {
	local path="${1}"

	local lang
	for lang in ${path}/*.po; do
		lang="$(basename "${lang}")"
		echo "${lang%*.po}"
	done | sort -u > "${path}/LINGUAS"
}

contributors() {
	local commits name

	git shortlog --summary --numbered | while read -r commits name; do
		echo "${name}"
	done | grep -vE -e "^(alpha197|morlix|root|ummeegge)$" -e "via Development$" -e "@" -e "#$"
}

update_contributors() {
	echo -n "Updating list of contributors"

	local contributors="$(contributors | paste -sd , - | sed -e "s/,/&\\\\n/g")"

	# Edit contributors into credits.cgi
	local tmp="$(mktemp)"

	awk "/<!-- CONTRIBUTORS -->/{ p=1; print; printf \"${contributors}\n\"}/<!-- END -->/{ p=0 } !p" \
		< "${BASEDIR}/html/cgi-bin/credits.cgi" > "${tmp}"

	# Copy back modified content
	cat "${tmp}" > "${BASEDIR}/html/cgi-bin/credits.cgi"
	unlink "${tmp}"

	print_status DONE
	return 0
}

# Download sources
download_sources() {
	local file
	local pkg

	local failed_packages=()

	# Walk through all files in LFS
	for file in "${BASEDIR}/lfs/"*; do
		pkg="${file##*/}"

		# Skip some packages
		case "${pkg}" in
			Config)
				continue
				;;
		esac

		# Run the common check
		lfsmakecommoncheck "${pkg}"
		[ $? == 1 ] && continue

		# Download and check the package
		if ! make_pkg --network "${pkg}" download b2; then
			failed_packages+=( "${pkg}" )
			print_status FAIL
			continue
		fi

		print_status DONE
	done

	# Fail if we could not download/verify all packages
	if [ "${#failed_packages[@]}" -gt 0 ]; then
		exiterror "Failed to download or verify some packages: ${failed_packages[@]}"
	fi
}

# Download the toolchain
download_toolchain() {
	local toolchain="${1}"

	# Do nothing if the toolchain has already been downloaded
	if [ -e "${TOOLCHAIN_DIR}/${toolchain}" ]; then
		return 0
	fi

	# Ensure the directory exists
	mkdir -p "${TOOLCHAIN_DIR}"

	# Create a temporary directory
	local tmp="$(mktemp -d)"

	# Make the name for the checksum file
	local checksums="${toolchain/.tar.zst/.b2}"

	# Download the toolchain and checksum files
	if ! wget --quiet --directory-prefix="${tmp}" \
			"${TOOLCHAIN_URL}/${toolchain}" \
			"${TOOLCHAIN_URL}/${checksums}"; then
		# Cleanup
		rm -rf "${tmp}"

		return 1
	fi

	# Check integrity
	if ! cd "${tmp}" && b2sum --quiet --check "${checksums}"; then
		# Cleanup
		rm -rf "${tmp}"

		return 1
	fi

	# Everything is good, move the files to their destination
	if ! mv \
			"${tmp}/${toolchain}" \
			"${tmp}/${checksums}" \
			"${TOOLCHAIN_DIR}"; then
		# Cleanup
		rm -rf "${tmp}"

		return 1
	fi

	# Cleanup
	rm -rf "${tmp}"

	return 0
}

# Extracts the toolchain
extract_toolchain() {
	local toolchain="${1}"

	local build_dir="${BUILD_DIR#${BASEDIR}/}"
	local log_dir="${LOG_DIR#${BASEDIR}/}"

	local args=(
		# Extract
		"ax"

		# The file to extract
		"-f" "${TOOLCHAIN_DIR}/${toolchain}"

		# The destination
		"-C" "${BASEDIR}"

		# Transform any older toolchains
		"--transform" "s@^build/@${build_dir}/@"
		"--transform" "s@^log/@${log_dir}/@"
	)

	# Extract the toolchain
	tar "${args[@]}" || return $?
}

# Compresses the toolchain
compress_toolchain() {
	local toolchain="${1}"

	log "Creating toolchain image for ${BUILD_ARCH}"

	# Create a temporary directory
	local tmp="$(mktemp -d)"

	# Make the name for the checksum file
	local checksums="${toolchain/.tar.zst/.b2}"

	local build_dir="${BUILD_DIR#${BASEDIR}/}"
	local log_dir="${LOG_DIR#${BASEDIR}/}"

	local args=(
		"--create"

		# Filter through zstd with custom options
		"-I" "zstd ${ZSTD_OPT[*]}"

		# Write to the temporary directory
		"-f" "${tmp}/${toolchain}"

		# Start in the base directory
		"-C" "${BASEDIR}"

		# Exclude the build logs
		"--exclude" "${log_dir}/_build.*.log"

		# Include /bin/sh
		"${build_dir}/bin/sh"

		# Include the /tools_${BUILD_ARCH} directory
		"${build_dir}/${TOOLS_DIR}"

		# Include the log directory
		"${log_dir}"
	)

	# Create the archive
	if ! tar "${args[@]}"; then
		# Cleanup
		rm -rf "${tmp}"

		return 1
	fi

	# Change to the temporary directory
	pushd "${tmp}" &>/dev/null

	# Create the checksums
	if ! b2sum "${toolchain}" > "${tmp}/${checksums}"; then
		popd &>/dev/null

		# Cleanup
		rm -rf "${tmp}"

		return 1
	fi

	popd &>/dev/null

	# Everything is good, move the files to their destination
	if ! mv \
			"${tmp}/${toolchain}" \
			"${tmp}/${checksums}" \
			"${TOOLCHAIN_DIR}"; then
		# Cleanup
		rm -rf "${tmp}"

		return 1
	fi

	return 0
}

build_toolchain() {
	local gcc=$(type -p gcc)
	if [ -z "${gcc}" ]; then
		exiterror "Could not find GCC. You will need a working build enviroment in order to build the toolchain."
	fi

	# Check ${TOOLS_DIR} symlink
	if [ -h "${TOOLS_DIR}" ]; then
		rm -f "${TOOLS_DIR}"
	fi

	if [ ! -e "${TOOLS_DIR}" ]; then
		ln -s "${BUILD_DIR}${TOOLS_DIR}" "${TOOLS_DIR}"
	fi

	if [ ! -h "${TOOLS_DIR}" ]; then
		exiterror "Could not create ${TOOLS_DIR} symbolic link"
	fi

	local LOGFILE="${LOG_DIR}/_build.toolchain.log"

	lfsmake1 stage1
	lfsmake1 binutils			PASS=1
	lfsmake1 gcc			PASS=1
	lfsmake1 linux			HEADERS=1
	lfsmake1 glibc
	lfsmake1 libxcrypt
	lfsmake1 gcc			PASS=L
	lfsmake1 zlib-ng
	lfsmake1 binutils			PASS=2
	lfsmake1 gcc			PASS=2
	lfsmake1 zstd
	lfsmake1 ccache
	lfsmake1 tcl
	lfsmake1 expect
	lfsmake1 dejagnu
	lfsmake1 pkg-config
	lfsmake1 ncurses
	lfsmake1 bash
	lfsmake1 bzip2
	lfsmake1 automake
	lfsmake1 coreutils
	lfsmake1 diffutils
	lfsmake1 findutils
	lfsmake1 gawk
	lfsmake1 gettext
	lfsmake1 grep
	lfsmake1 gzip
	lfsmake1 m4
	lfsmake1 make
	lfsmake1 patch
	lfsmake1 perl
	lfsmake1 python3
	lfsmake1 sed
	lfsmake1 tar
	lfsmake1 texinfo
	lfsmake1 xz
	lfsmake1 bison
	lfsmake1 flex
	lfsmake1 fake-environ
	CUSTOM_PATH="${PATH}" lfsmake1 strip
	lfsmake1 cleanup-toolchain
}

build_system() {
	local LOGFILE="${LOG_DIR}/_build.${SNAME}.log"

	lfsmake2 --enable-toolchain stage2
	lfsmake2 --enable-toolchain linux			HEADERS=1
	lfsmake2 --enable-toolchain man-pages
	lfsmake2 --enable-toolchain glibc
	lfsmake2 --enable-toolchain tzdata
	lfsmake2 --enable-toolchain cleanup-toolchain
	lfsmake2 --enable-toolchain zlib-ng
	[ "${BUILD_ARCH}" = "riscv64" ] && lfsmake2 --enable-toolchain gcc PASS=A
	lfsmake2 --enable-toolchain zstd
	lfsmake2 --enable-toolchain autoconf
	lfsmake2 --enable-toolchain autoconf-archive
	lfsmake2 --enable-toolchain automake
	lfsmake2 --enable-toolchain help2man
	lfsmake2 --enable-toolchain libtool
	lfsmake2 --enable-toolchain binutils
	lfsmake2 --enable-toolchain gmp
	lfsmake2 --enable-toolchain mpfr
	lfsmake2 --enable-toolchain libmpc
	lfsmake2 --enable-toolchain pkg-config
	lfsmake2 --enable-toolchain libxcrypt
	lfsmake2 --enable-toolchain file
	lfsmake2 --enable-toolchain gcc
	lfsmake2 --enable-toolchain attr
	lfsmake2 --enable-toolchain acl
	lfsmake2 --enable-toolchain sed
	lfsmake2 --enable-toolchain berkeley
	lfsmake2 --enable-toolchain coreutils
	lfsmake2 --enable-toolchain iana-etc
	lfsmake2 --enable-toolchain m4
	lfsmake2 --enable-toolchain bison
	lfsmake2 --enable-toolchain ncurses
	lfsmake2 --enable-toolchain perl
	lfsmake2 --enable-toolchain readline
	lfsmake2 --enable-toolchain bzip2
	lfsmake2 --enable-toolchain xz
	lfsmake2 --enable-toolchain lzip
	lfsmake2 --enable-toolchain pcre
	lfsmake2 --enable-toolchain pcre2
	lfsmake2 --enable-toolchain gettext
	lfsmake2 --enable-toolchain bash
	lfsmake2 --enable-toolchain diffutils
	lfsmake2 --enable-toolchain ed
	lfsmake2 --enable-toolchain findutils
	lfsmake2 --enable-toolchain flex
	lfsmake2 --enable-toolchain gawk
	lfsmake2 --enable-toolchain go
	lfsmake2 --enable-toolchain grep
	lfsmake2 --enable-toolchain groff
	lfsmake2 --enable-toolchain gperf
	lfsmake2 --enable-toolchain gzip
	lfsmake2 --enable-toolchain hostname
	lfsmake2 --enable-toolchain whois
	lfsmake2 --enable-toolchain kbd
	lfsmake2 --enable-toolchain less
	lfsmake2 --enable-toolchain procps
	lfsmake2 --enable-toolchain make
	lfsmake2 --enable-toolchain libpipeline
	lfsmake2 --enable-toolchain man
	lfsmake2 --enable-toolchain net-tools
	lfsmake2 --enable-toolchain patch
	lfsmake2 --enable-toolchain psmisc
	lfsmake2 --enable-toolchain shadow
	lfsmake2 --enable-toolchain sysklogd
	lfsmake2 --enable-toolchain sysvinit
	lfsmake2 --enable-toolchain tar
	lfsmake2 --enable-toolchain texinfo
	lfsmake2 --enable-toolchain util-linux
	lfsmake2 --enable-toolchain vim
	lfsmake2 --enable-toolchain e2fsprogs
	lfsmake2 --enable-toolchain jq

	# From here, build without having the toolchain available
	lfsmake2 configroot
	lfsmake2 initscripts
	lfsmake2 backup
	lfsmake2 rust
	lfsmake2 openssl
	lfsmake2 popt
	lfsmake2 libedit
	lfsmake2 expat
	lfsmake2 libffi
	lfsmake2 gdbm
	lfsmake2 sqlite
	lfsmake2 python3
	lfsmake2 python3-wheel
	lfsmake2 python3-toml
	lfsmake2 python3-setuptools
	lfsmake2 python3-pyproject2setuppy
	lfsmake2 python3-packaging
	lfsmake2 python3-pep517
	lfsmake2 python3-build
	lfsmake2 python3-install
	lfsmake2 python3-urllib3
	lfsmake2 python3-charset-normalizer
	lfsmake2 python3-idna
	lfsmake2 python3-certifi
	lfsmake2 python3-requests
	lfsmake2 python3-docutils
	lfsmake2 python3-flit
	lfsmake2 python3-more_itertools
	lfsmake2 ninja
	lfsmake2 meson
	lfsmake2 pam
	lfsmake2 libcap
	lfsmake2 libcap-ng
	lfsmake2 libpcap
	lfsmake2 ppp
	lfsmake2 pptp
	lfsmake2 unzip
	lfsmake2 which
	lfsmake2 bc
	lfsmake2 cpio
	lfsmake2 libaio
	lfsmake2 freetype
	lfsmake2 libmnl
	lfsmake2 libnfnetlink
	lfsmake2 libnetfilter_queue
	lfsmake2 libnetfilter_conntrack
	lfsmake2 libnetfilter_cthelper
	lfsmake2 libnetfilter_cttimeout
	lfsmake2 iptables
	lfsmake2 iproute2
	lfsmake2 screen
	lfsmake2 elfutils
	lfsmake2 libconfig
	lfsmake2 curl
	lfsmake2 libarchive
	lfsmake2 cmake
	lfsmake2 json-c
	lfsmake2 tcl
	lfsmake2 python3-MarkupSafe
	lfsmake2 python3-Jinja2
	lfsmake2 kmod
	lfsmake2 udev
	lfsmake2 libusb
	lfsmake2 mdadm
	lfsmake2 dracut-ng
	lfsmake2 lvm2
	lfsmake2 multipath-tools
	lfsmake2 glib
	lfsmake2 json-glib
	lfsmake2 libgudev
	lfsmake2 libgpg-error
	lfsmake2 libgcrypt
	lfsmake2 libassuan
	lfsmake2 nettle
	lfsmake2 libsodium
	lfsmake2 libevent2
	lfsmake2 apr
	lfsmake2 aprutil
	lfsmake2 unbound
	lfsmake2 libtasn1
	lfsmake2 libunistring
	lfsmake2 gnutls
	lfsmake2 libuv
	lfsmake2 liburcu
	lfsmake2 bind
	lfsmake2 dhcp
	lfsmake2 dhcpcd
	lfsmake2 boost
	lfsmake2 linux-atm
	lfsmake2 libqmi
	lfsmake2 c-ares
	lfsmake2 rust-dissimilar
	lfsmake2 rust-cfg-if
	lfsmake2 rust-libc
	lfsmake2 rust-getrandom
	lfsmake2 rust-typenum
	lfsmake2 rust-version-check
	lfsmake2 rust-generic-array
	lfsmake2 rust-crypto-common
	lfsmake2 rust-cipher
	lfsmake2 rust-hex
	lfsmake2 rust-unicode-xid
	lfsmake2 rust-unicode-ident
	lfsmake2 rust-proc-macro2
	lfsmake2 rust-quote
	lfsmake2 rust-syn-1.0.109
	lfsmake2 rust-syn
	lfsmake2 rust-home
	lfsmake2 rust-lazy-static
	lfsmake2 rust-memchr
	lfsmake2 rust-aho-corasick
	lfsmake2 rust-regex-syntax
	lfsmake2 rust-regex
	lfsmake2 rust-ucd-trie
	lfsmake2 rust-pest
	lfsmake2 rust-semver-parser
	lfsmake2 rust-semver
	lfsmake2 rust-same-file
	lfsmake2 rust-walkdir
	lfsmake2 rust-dirs
	lfsmake2 rust-toolchain_find
	lfsmake2 rust-serde_derive
	lfsmake2 rust-serde
	lfsmake2 rust-itoa
	lfsmake2 rust-ryu
	lfsmake2 rust-serde_json
	lfsmake2 rust-synstructure
	lfsmake2 rust-block-buffer
	lfsmake2 rust-digest
	lfsmake2 rust-ppv-lite86
	lfsmake2 rust-rand_core
	lfsmake2 rust-rand_core-0.4.2
	lfsmake2 rust-rand_core-0.3.1
	lfsmake2 rust-rand_chacha
	lfsmake2 rust-rand_hc
	lfsmake2 rust-rand
	lfsmake2 rust-rdrand
	lfsmake2 rust-rand-0.4
	lfsmake2 rust-log
	lfsmake2 rust-num_cpus
	lfsmake2 rust-crossbeam-utils
	lfsmake2 rust-autocfg
	lfsmake2 rust-memoffset
	lfsmake2 rust-scopeguard
	lfsmake2 rust-crossbeam-epoch
	lfsmake2 rust-crossbeam-deque
	lfsmake2 rust-either
	lfsmake2 rust-crossbeam-channel
	lfsmake2 rust-rayon-core
	lfsmake2 rust-rayon
	lfsmake2 rust-remove_dir_all
	lfsmake2 rust-tempdir
	lfsmake2 rust-glob
	lfsmake2 rust-once_cell
	lfsmake2 rust-termcolor
	lfsmake2 rust-serde_spanned
	lfsmake2 rust-toml_datetime
	lfsmake2 rust-equivalent
	lfsmake2 rust-allocator-api2
	lfsmake2 rust-foldhash
	lfsmake2 rust-hashbrown
	lfsmake2 rust-indexmap
	lfsmake2 rust-winnow
	lfsmake2 rust-toml_edit
	lfsmake2 rust-toml
	lfsmake2 rust-target-triple
	lfsmake2 rust-trybuild
	lfsmake2 rust-unindent
	lfsmake2 rust-proc-macro-hack
	lfsmake2 rust-indoc-impl
	lfsmake2 rust-indoc-impl-0.3.6
	lfsmake2 rust-indoc
	lfsmake2 rust-indoc-0.3.6
	lfsmake2 rust-instant
	lfsmake2 rust-lock_api
	lfsmake2 rust-smallvec
	lfsmake2 rust-parking_lot_core
	lfsmake2 rust-parking_lot
	lfsmake2 rust-paste-impl
	lfsmake2 rust-paste
	lfsmake2 rust-paste-0.1.18
	lfsmake2 rust-ctor
	lfsmake2 rust-ghost
	lfsmake2 rust-inventory-impl
	lfsmake2 rust-inventory
	lfsmake2 rust-pyo3-build-config
	lfsmake2 rust-pyo3-macros-backend
	lfsmake2 rust-pyo3-macros
	lfsmake2 rust-pyo3
	lfsmake2 rust-num-traits
	lfsmake2 rust-num-integer
	lfsmake2 rust-num_threads
	lfsmake2 rust-time
	lfsmake2 rust-iana-time-zone
	lfsmake2 rust-chrono
	lfsmake2 rust-asn1_derive
	lfsmake2 rust-asn1
	lfsmake2 rust-proc-macro-error-attr
	lfsmake2 rust-proc-macro-error
	lfsmake2 rust-Inflector
	lfsmake2 rust-ouroboros_macro
	lfsmake2 rust-aliasable
	lfsmake2 rust-stable_deref_trait
	lfsmake2 rust-ouroboros
	lfsmake2 rust-base64
	lfsmake2 rust-pem
	lfsmake2 gdb
	lfsmake2 grub
	lfsmake2 mandoc
	lfsmake2 efivar
	lfsmake2 efibootmgr
	lfsmake2 p11-kit
	lfsmake2 ca-certificates
	lfsmake2 fireinfo
	lfsmake2 libnet
	lfsmake2 libnl-3
	lfsmake2 libidn2
	lfsmake2 nasm
	lfsmake2 libexif
	lfsmake2 libjpeg
	lfsmake2 libpng
	lfsmake2 gd
	lfsmake2 slang
	lfsmake2 newt
	lfsmake2 libsmooth
	lfsmake2 pciutils
	lfsmake2 usbutils
	lfsmake2 libxml2
	lfsmake2 libxslt
	lfsmake2 perl-BerkeleyDB
	lfsmake2 cyrus-sasl
	lfsmake2 openldap
	lfsmake2 apache2
	lfsmake2 web-user-interface
	lfsmake2 flag-icons
	lfsmake2 jquery
	lfsmake2 bootstrap
	lfsmake2 arping
	lfsmake2 beep
	lfsmake2 libssh
	lfsmake2 libinih
	lfsmake2 xorriso
	lfsmake2 dosfstools
	lfsmake2 exfatprogs
	lfsmake2 reiserfsprogs
	lfsmake2 xfsprogs
	lfsmake2 sysfsutils
	lfsmake2 fuse
	lfsmake2 ntfs-3g
	lfsmake2 ethtool
	lfsmake2 fcron
	lfsmake2 wireguard-tools
	lfsmake2 perl-ExtUtils-PkgConfig
	lfsmake2 perl-GD
	lfsmake2 perl-GD-Graph
	lfsmake2 perl-GD-TextUtil
	lfsmake2 perl-Device-SerialPort
	lfsmake2 perl-Device-Modem
	lfsmake2 perl-Parse-Yapp
	lfsmake2 perl-Data-UUID
	lfsmake2 perl-Try-Tiny
	lfsmake2 perl-HTTP-Message
	lfsmake2 perl-HTTP-Date
	lfsmake2 gnupg
	lfsmake2 hdparm
	lfsmake2 whatmask
	lfsmake2 libtirpc
	lfsmake2 conntrack-tools
	lfsmake2 iputils
	lfsmake2 l7-protocols
	lfsmake2 hwdata
	lfsmake2 logrotate
	lfsmake2 logwatch
	lfsmake2 misc-progs
	lfsmake2 nano
	lfsmake2 perl-URI
	lfsmake2 perl-CGI
	lfsmake2 perl-Switch
	lfsmake2 perl-HTML-Tagset
	lfsmake2 perl-HTML-Parser
	lfsmake2 perl-HTML-Template
	lfsmake2 perl-libwww
	lfsmake2 perl-LWP-Protocol-https
	lfsmake2 perl-Net-HTTP
	lfsmake2 perl-Net-DNS
	lfsmake2 perl-Net-IPv4Addr
	lfsmake2 perl-Net_SSLeay
	lfsmake2 perl-IO-Stringy
	lfsmake2 perl-IO-Socket-SSL
	lfsmake2 perl-Unix-Syslog
	lfsmake2 perl-Mail-Tools
	lfsmake2 perl-MIME-Tools
	lfsmake2 perl-Net-Server
	lfsmake2 perl-Canary-Stability
	lfsmake2 perl-Convert-TNEF
	lfsmake2 perl-Convert-UUlib
	lfsmake2 perl-Archive-Zip
	lfsmake2 perl-Text-Tabs+Wrap
	lfsmake2 perl-XML-Parser
	lfsmake2 perl-Crypt-PasswdMD5
	lfsmake2 perl-Net-Telnet
	lfsmake2 perl-Capture-Tiny
	lfsmake2 perl-Config-AutoConf
	lfsmake2 perl-File-LibMagic
	lfsmake2 perl-Object-Tiny
	lfsmake2 perl-Archive-Peek-Libarchive
	lfsmake2 python3-inotify
	lfsmake2 python3-daemon
	lfsmake2 ntp
	lfsmake2 openssh
	lfsmake2 fontconfig
	lfsmake2 prompt
	lfsmake2 dejavu-fonts-ttf
	lfsmake2 ubuntu-font-family
	lfsmake2 freefont
	lfsmake2 pixman
	lfsmake2 cairo
	lfsmake2 harfbuzz
	lfsmake2 fribidi
	lfsmake2 pango
	lfsmake2 rrdtool
	lfsmake2 setup
	lfsmake2 jansson
	lfsmake2 yaml
	lfsmake2 colm
	lfsmake2 ragel
	lfsmake2 vectorscan
	lfsmake2 suricata
	lfsmake2 ids-ruleset-sources
	lfsmake2 ipblocklist-sources
	lfsmake2 squid
	lfsmake2 squidguard
	lfsmake2 calamaris
	lfsmake2 tcpdump
	lfsmake2 traceroute
	lfsmake2 wireless
	lfsmake2 pakfire
	lfsmake2 lz4
	lfsmake2 lzo
	lfsmake2 openvpn
	lfsmake2 mpage
	lfsmake2 dbus
	lfsmake2 intltool
	lfsmake2 libdaemon
	lfsmake2 avahi
	lfsmake2 libtalloc
	lfsmake2 cifs-utils
	lfsmake2 krb5
	lfsmake2 rpcsvc-proto
	lfsmake2 lmdb
	lfsmake2 samba
	lfsmake2 iniparser
	lfsmake2 netatalk
	lfsmake2 sudo
	lfsmake2 mc
	lfsmake2 wget
	lfsmake2 bridge-utils
	lfsmake2 smartmontools
	lfsmake2 htop
	lfsmake2 chkconfig
	lfsmake2 postfix
	lfsmake2 fetchmail
	lfsmake2 clamav
	lfsmake2 perl-NetAddr-IP
	lfsmake2 dma
	lfsmake2 alsa
	lfsmake2 guardian
	lfsmake2 libid3tag
	lfsmake2 libmad
	lfsmake2 libogg
	lfsmake2 libvorbis
	lfsmake2 flac
	lfsmake2 lame
	lfsmake2 soxr
	lfsmake2 libshout
	lfsmake2 gnump3d
	lfsmake2 libxxhash
	lfsmake2 rsync
	lfsmake2 rpcbind
	lfsmake2 keyutils
	lfsmake2 nfs
	lfsmake2 ncat
	lfsmake2 nmap
	lfsmake2 etherwake
	lfsmake2 bwm-ng
	lfsmake2 sysstat
	lfsmake2 strongswan
	lfsmake2 rng-tools
	lfsmake2 lsof
	lfsmake2 lm_sensors
	lfsmake2 libstatgrab
	lfsmake2 liboping
	lfsmake2 netsnmpd
	lfsmake2 nut
	lfsmake2 collectd
	lfsmake2 git
	lfsmake2 linux-firmware
	lfsmake2 dvb-firmwares
	lfsmake2 zd1211-firmware
	lfsmake2 rpi-firmware
	lfsmake2 intel-microcode
	lfsmake2 pcengines-apu-firmware
	lfsmake2 elinks
	lfsmake2 igmpproxy
	lfsmake2 opus
	lfsmake2 python3-pyparsing
	lfsmake2 spice-protocol
	lfsmake2 spice
	lfsmake2 sdl2
	lfsmake2 libusbredir
	lfsmake2 libseccomp
	lfsmake2 libslirp
	lfsmake2 dtc
	lfsmake2 python3-tomli
	lfsmake2 qemu
	lfsmake2 nagios_nrpe
	lfsmake2 nagios-plugins
	lfsmake2 observium-agent
	lfsmake2 ebtables
	lfsmake2 faad2
	lfsmake2 alac
	lfsmake2 ffmpeg
	lfsmake2 vdr
	lfsmake2 vdr_streamdev
	lfsmake2 vdr_epgsearch
	lfsmake2 vdr_dvbapi
	lfsmake2 vdr_eepg
	lfsmake2 w_scan
	lfsmake2 fmt
	lfsmake2 mpd
	lfsmake2 libmpdclient
	lfsmake2 mpc
	lfsmake2 perl-Net-CIDR-Lite
	lfsmake2 perl-Net-SMTP-SSL
	lfsmake2 perl-Authen-SASL
	lfsmake2 perl-MIME-Lite
	lfsmake2 perl-Email-Date-Format
	lfsmake2 vnstat
	lfsmake2 iw
	lfsmake2 wpa_supplicant
	lfsmake2 hostapd
	lfsmake2 syslinux
	lfsmake2 tftpd
	lfsmake2 apcupsd
	lfsmake2 fireperf
	lfsmake2 iperf
	lfsmake2 iperf3
	lfsmake2 7zip
	lfsmake2 lynis
	lfsmake2 sshfs
	lfsmake2 utfcpp
	lfsmake2 taglib
	lfsmake2 perl-gettext
	lfsmake2 perl-Sort-Naturally
	lfsmake2 vdradmin
	lfsmake2 perl-DBI
	lfsmake2 perl-DBD-SQLite
	lfsmake2 perl-File-ReadBackwards
	lfsmake2 openvmtools
	lfsmake2 joe
	lfsmake2 monit
	lfsmake2 watchdog
	lfsmake2 usb_modeswitch
	lfsmake2 usb_modeswitch_data
	lfsmake2 zerofree
	lfsmake2 minicom
	lfsmake2 ddrescue
	lfsmake2 parted
	lfsmake2 swig
	lfsmake2 python3-pyelftools
	lfsmake2 u-boot
	lfsmake2 wireless-regdb
	lfsmake2 ddns
	lfsmake2 python3-pycparser
	lfsmake2 python3-typing-extensions
	lfsmake2 python3-semantic-version
	lfsmake2 python3-setuptools-scm
	lfsmake2 python3-setuptools-rust
	lfsmake2 python3-six
	lfsmake2 python3-dateutil
	lfsmake2 python3-jmespath
	lfsmake2 python3-colorama
	lfsmake2 python3-yaml
	lfsmake2 python3-s3transfer
	lfsmake2 python3-rsa
	lfsmake2 python3-pyasn1
	lfsmake2 python3-botocore
	lfsmake2 python3-cffi
	lfsmake2 python3-cryptography
	lfsmake2 python3-circuitbreaker
	lfsmake2 python3-pytz
	lfsmake2 python3-click
	lfsmake2 python3-arrow
	lfsmake2 python3-terminaltables
	lfsmake2 python3-pkgconfig
	lfsmake2 python3-msgpack
	lfsmake2 python3-editables
	lfsmake2 python3-pathspec
	lfsmake2 python3-pluggy
	lfsmake2 python3-calver
	lfsmake2 python3-trove-classifiers
	lfsmake2 python3-hatchling
	lfsmake2 python3-hatch-vcs
	lfsmake2 python3-hatch-fancy-pypi-readme
	lfsmake2 python3-attrs
	lfsmake2 python3-sniffio
	lfsmake2 python3-sortedcontainers
	lfsmake2 python3-outcome
	lfsmake2 python3-async_generator
	lfsmake2 python3-flit_scm
	lfsmake2 python3-exceptiongroup
	lfsmake2 python3-trio
	lfsmake2 python3-pyfuse3
	lfsmake2 python3-pillow
	lfsmake2 python3-reportlab
	lfsmake2 aws-cli
	lfsmake2 oci-python-sdk
	lfsmake2 oci-cli
	lfsmake2 transmission
	lfsmake2 mtr
	lfsmake2 minidlna
	lfsmake2 acpid
	lfsmake2 fping
	lfsmake2 telnet
	lfsmake2 xinetd
	lfsmake2 stress
	lfsmake2 sarg
	lfsmake2 nginx
	lfsmake2 sysbench
	lfsmake2 strace
	lfsmake2 ltrace
	lfsmake2 ipfire-netboot
	lfsmake2 keepalived
	lfsmake2 ipvsadm
	lfsmake2 perl-Carp-Clan
	lfsmake2 perl-Date-Calc
	lfsmake2 perl-Date-Manip
	lfsmake2 perl-File-Tail
	lfsmake2 perl-TimeDate
	lfsmake2 swatch
	lfsmake2 tor
	lfsmake2 wavemon
	lfsmake2 iptraf-ng
	lfsmake2 iotop
	lfsmake2 stunnel
	lfsmake2 bacula
	lfsmake2 perl-Font-TTF
	lfsmake2 perl-IO-String
	lfsmake2 perl-PDF-API2
	lfsmake2 proxy-accounting
	lfsmake2 tmux
	lfsmake2 perl-Text-CSV_XS
	lfsmake2 lua
	lfsmake2 haproxy
	lfsmake2 ipset
	lfsmake2 dnsdist
	lfsmake2 bird
	lfsmake2 libyang
	lfsmake2 abseil-cpp
	lfsmake2 protobuf
	lfsmake2 protobuf-c
	lfsmake2 frr
	lfsmake2 dmidecode
	lfsmake2 mcelog
	lfsmake2 socat
	lfsmake2 libtpms
	lfsmake2 expect
	lfsmake2 swtpm
	lfsmake2 libpciaccess
	lfsmake2 ovmf
	lfsmake2 libvirt
	lfsmake2 freeradius
	lfsmake2 perl-common-sense
	lfsmake2 perl-inotify2
	lfsmake2 perl-Net-IP
	lfsmake2 wio
	lfsmake2 iftop
	lfsmake2 mdns-repeater
	lfsmake2 i2c-tools
	lfsmake2 nss-myhostname
	lfsmake2 dehydrated
	lfsmake2 libplist
	lfsmake2 nqptp
	lfsmake2 shairport-sync
	lfsmake2 borgbackup
	lfsmake2 knot
	lfsmake2 spectre-meltdown-checker
	lfsmake2 zabbix_agentd
	lfsmake2 flashrom
	lfsmake2 firmware-update
	lfsmake2 ruby
	lfsmake2 asciidoctor
	lfsmake2 speexdsp
	lfsmake2 tshark
	lfsmake2 speedtest-cli
	lfsmake2 amazon-ssm-agent
	lfsmake2 libloc
	lfsmake2 ncdu
	lfsmake2 lshw
	lfsmake2 libcdada
	lfsmake2 pmacct
	lfsmake2 squid-asnbl
	lfsmake2 qemu-ga
	lfsmake2 gptfdisk
	lfsmake2 oath-toolkit
	lfsmake2 qrencode
	lfsmake2 perl-File-Remove
	lfsmake2 perl-Module-Build
	lfsmake2 perl-Module-ScanDeps
	lfsmake2 perl-YAML-Tiny
	lfsmake2 perl-Module-Install
	lfsmake2 perl-Imager
	lfsmake2 perl-Imager-QRCode
	lfsmake2 perl-MIME-Base32
	lfsmake2 perl-URI-Encode
	lfsmake2 rsnapshot
	lfsmake2 mympd
	lfsmake2 wsdd
	lfsmake2 btrfs-progs
	lfsmake2 inotify-tools
	lfsmake2 grub-btrfs
	lfsmake2 fort-validator
	lfsmake2 arpwatch
	lfsmake2 suricata-reporter

	lfsmake2 linux
	lfsmake2 rtl8812au
	lfsmake2 linux-initrd

	lfsmake2 memtest

	# Build the installer
	lfsmake2 installer

	# Build images
	lfsmake2 cdrom
	lfsmake2 flash-images
	lfsmake2 core-updates
}

build_packages() {
	local LOGFILE="${LOG_DIR}/_build.packages.log"

	# Build packages
	print_headline "Building Packages"

	local path
	local -A pkgs=()
	local pkg

	# Collect all packages
	for path in \
			"${BASEDIR}/config/rootfiles/packages/"* \
			"${BASEDIR}/config/rootfiles/packages/${BUILD_ARCH}"/*; do
		# Skip directories
		if [ -d "${path}" ]; then
			continue
		fi

		pkgs["${path##*/}"]="${path}"
	done

	# Package them all
	for pkg in ${!pkgs[@]}; do
		ipfiredist "${pkg}"
	done
}

# This function will re-execute a command in a new namespace
exec_in_namespace() {
	# Nothing to do if we are already in a new namespace
	if [ -n "${IN_NAMESPACE}" ]; then
		return 0
	fi

	# Forward any configuration
	local args=(
		"--target=${BUILD_ARCH}"
	)

	IN_NAMESPACE=1 \
	exec unshare \
		--mount \
		--propagation=private \
		"${0}" "${args[@]}" "$@"
}

check_for_missing_rootfiles() {
	print_headline "Checking for missing rootfiles..."

	local file
	for file in ${LOG_DIR}/*_missing_rootfile; do
		[ -e "${file}" ] || continue

		file="${file##*/}"
		file="${file/_missing_rootfile/}";

		print_line "${file} is missing a rootfile"
		print_status FAIL
	done

	return 0
}

check_rootfiles_for_arch() {
	local arch="${1}"

	local args=(
		# Search path
		"${BASEDIR}/config/rootfiles"

		# Exclude old core updates
		"--exclude-dir" "oldcore"

		# Ignore the update scripts
		"--exclude" "update.sh"
	)

	# A list of files that are not scanned
	# because they probably cause some false positives.
	local excluded_files=(
		abseil-cpp
		cmake
		gdb
		liburcu
		ovmf
		qemu
		rust-memchr
		rust-libc
		rust-ppv-lite86
		xfsprogs
	)

	# Exclude any architecture-specific directories
	local a
	for a in ${ARCHES[@]}; do
		args+=( "--exclude-dir" "${a}" )
	done

	# Exclude all excluded files
	local x
	for x in ${excluded_files[@]}; do
		args+=( "--exclude" "${x}" )
	done

	# Search for all files that contain the architecture
	local files=(
		$(grep --files-with-matches -r "^.*${arch}" "${args[@]}")
	)

	local file
	for file in ${files[@]}; do
		print_line "${file} contains ${arch}"
		print_status FAIL
	done

	return "${#files[@]}"
}

check_rootfiles_for_pattern() {
	local pattern="${1}"
	local message="${2}"

	local args=(
		# Search path
		"${BASEDIR}/config/rootfiles"

		# Exclude old core updates
		"--exclude-dir" "oldcore"

		# Ignore the update scripts
		"--exclude" "update.sh"
	)

	if grep -r "${pattern}" "${args[@]}"; then
		if [ -n "${message}" ]; then
			print_line "${message}"
			print_status FAIL
		else
			print_file "Files matching '${pattern}' have been found in the rootfiles"
			print_status FAIL
		fi
		return 1
	fi

	return 0
}

check_rootfiles() {
	local failed=0

	print_headline "Checking for rootfile consistency..."

	# Check for changes
	if ! check_rootfiles_for_pattern "^[\+\-]" \
			"Rootfiles have changed in them"; then
		failed=1
	fi

	# Check for /etc/init.d
	if ! check_rootfiles_for_pattern "^etc/init\.d/" \
			"/etc/init.d/* has been found. Please replace by /etc/rc.d/init.d"; then
		failed=1
	fi

	# Check for /var/run
	if ! check_rootfiles_for_pattern "^var/run/.*" \
			"You cannot ship files in /var/run as it is a ramdisk"; then
		failed=1
	fi

	# Check architectures
	local arch
	for arch in ${ARCHES[@]}; do
		check_rootfiles_for_arch "${arch}" || failed=$?
	done

	# Return the error
	return ${failed}
}

check_changed_rootfiles() {
	local files=(
		$(grep --files-with-matches -r "^+" "${LOG_DIR}" --exclude="_*" | sort)
	)

	# If we have no matches, there is nothing to do
	[ "${#files[@]}" -eq 0 ] && return 0

	print_line "Packages have created new files"
	print_status WARN

	local file
	for file in ${files[@]}; do
		print_line "  ${file##*/}"
		print_status WARN
	done

	return 0
}

# Set BASEDIR
readonly BASEDIR="$(find_base)"

# Get some information about the host system
SYSTEM_PROCESSORS="$(system_processors)"
SYSTEM_MEMORY="$(system_memory)"

# Default settings
BUILD_ARCH="${HOST_ARCH}"
CCACHE_CACHE_SIZE="4G"

# Load configuration file
if [ -f .config ]; then
	source .config
fi

# Parse any command line options (not commands)
while [ $# -gt 0 ]; do
	case "${1}" in
		--target=*)
			BUILD_ARCH="${1#--target=}"
			;;

		-*)
			exiterror "Unknown configuration option: ${1}"
			;;

		# Found a command, so exit options parsing
		*)
			break
			;;
	esac
	shift
done

# Check the architecture
case "${BUILD_ARCH}" in
	aarch64|x86_64|riscv64)
		;;

	*)
		exiterror "Unsupported architecture: ${BUILD_ARCH}"
		;;
esac

# Set build platform
case "${BUILD_ARCH}" in
	aarch64)
		BUILD_PLATFORM="arm"
		;;

	riscv64)
		BUILD_PLATFORM="riscv"
		;;

	x86_64)
		BUILD_PLATFORM="x86"
		;;
esac

# Configure the C compiler
CFLAGS=(
	# Optimize the code
	"-O2"

	# Do not compile in any debugging information
	"-g0"

	# Do not write temporary files
	"-pipe"

	# Enable all warnings
	"-Wall"

	# Enable exceptions
	"-fexceptions"

	# Compile place-independent code
	"-fPIC"

	# Fortify Source
	"-Wp,-U_FORTIFY_SOURCE"
	"-Wp,-D_FORTIFY_SOURCE=3"

	# Enable additional checks for C++ in glibc
	"-Wp,-D_GLIBCXX_ASSERTIONS"

	# Enable stack smashing protection
	"-fstack-protector-strong"

	# Enable stack clash protection
	"-fstack-clash-protection"
)

# Architecture-dependent compiler flags
case "${BUILD_ARCH}" in
	aarch64)
		CFLAGS+=(
			"-mbranch-protection=standard"
		)
		;;

	x86_64)
		CFLAGS+=(
			"-m64" "-mtune=generic" "-fcf-protection=full"
		)
		;;
esac

# Configure the Rust compiler
RUSTFLAGS=(
	"-Copt-level=3"
	"-Clink-arg=-Wl,-z,relro,-z,now"
	"-Ccodegen-units=1"
	"--cap-lints=warn"
)

# Configure the compiler tuple
CROSSTARGET="${BUILD_ARCH}-cross-linux-gnu"
BUILDTARGET="${BUILD_ARCH}-pc-linux-gnu"

# Use this as default PARALLELISM
DEFAULT_PARALLELISM="${SYSTEM_PROCESSORS}"

# Limit lauched ninja build jobs to computed parallel value
NINJAJOBS="${DEFAULT_PARALLELISM}"

# Configure XZ
XZ_OPT=(
	"-T0" "-8"
)

# Configure Zstandard
ZSTD_OPT=(
	"-T0" "-19" "--long"
)

# Set directories
readonly CACHE_DIR="${BASEDIR}/cache"
readonly TOOLCHAIN_DIR="${CACHE_DIR}/toolchains"
readonly CCACHE_DIR="${BASEDIR}/ccache/${BUILD_ARCH}/${TOOLCHAINVER}"
readonly BUILD_DIR="${BASEDIR}/build_${BUILD_ARCH}"
readonly IMAGES_DIR="${BASEDIR}/images_${BUILD_ARCH}"
readonly LOG_DIR="${BASEDIR}/log_${BUILD_ARCH}"
readonly PACKAGES_DIR="${IMAGES_DIR}/packages"
readonly TOOLS_DIR="/tools_${BUILD_ARCH}"

# Set URLs
readonly SOURCE_URL="https://source.ipfire.org/ipfire-2.x"
readonly TOOLCHAIN_URL="https://source.ipfire.org/toolchains"

# Set the LOGFILE
LOGFILE="${LOG_DIR}/_build.preparation.log"

# Ensure that some basic directories exist
mkdir -p "${CACHE_DIR}" "${LOG_DIR}"

# Toolchain Archive
readonly TOOLCHAIN="${SNAME}-${VERSION}-toolchain-${TOOLCHAINVER}-${BUILD_ARCH}.tar.zst"

# See what we're supposed to do
case "$1" in
build)
	START_TIME="${SECONDS}"

	# Launch in a new namespace
	exec_in_namespace "$@"

	# Prepare the environment
	prepareenv --required-space=8192

	# Check if the toolchain is available
	if [ ! -e "${BUILD_DIR}${TOOLS_DIR}/.toolchain-successful" ]; then
		# If we have the toolchain available, we extract it into the build environment
		if [ -r "${TOOLCHAIN_DIR}/${TOOLCHAIN}" ]; then
			print_headline "Packaged toolchain compilation"

			# Extract the toolchain
			if ! extract_toolchain "${TOOLCHAIN}"; then
				exiterror "Failed extracting the toolchain"
			fi

		# Otherwise perform a full toolchain compilation
		else
			print_headline "Full toolchain compilation"
			build_toolchain
		fi
	fi

	print_headline "Building ${NAME}"
	build_system

	# Build all packages
	build_packages

	# Check for missing rootfiles
	check_for_missing_rootfiles

	# Check for rootfile consistency
	if ! check_rootfiles; then
		exiterror "Rootfiles are inconsistent"
	fi

	check_changed_rootfiles

	print_build_summary $(( SECONDS - START_TIME ))
	;;
tail)
	tail -F \
		"${LOG_DIR}/_build.preparation.log" \
		"${LOG_DIR}/_build.toolchain.log" \
		"${LOG_DIR}/_build.${SNAME}.log" \
		"${LOG_DIR}/_build.packages.log" 2>/dev/null
	;;
shell)
	# Launch in a new namespace
	exec_in_namespace "$@"

	# enter a shell inside LFS chroot
	# may be used to changed kernel settings
	prepareenv --network
	entershell
	;;
check)
	# Check for rootfile consistency
	if ! check_rootfiles; then
		exiterror "Rootfiles are inconsistent"
	fi

	check_changed_rootfiles
	;;
clean)
	print_line "Cleaning build directory..."

	# Cleanup build files
	rm -rf \
		"${BUILD_DIR}" \
		"${IMAGES_DIR}" \
		"${LOG_DIR}"

	# Remove the /tools symlink
	if [ -h "${TOOLS_DIR}" ]; then
		rm -f "${TOOLS_DIR}"
	fi

	print_status DONE
	;;
downloadsrc)
	# Tell the user what we are about to do
	print_headline "Pre-loading all source files"

	# Download all sources
	download_sources
	;;
toolchain)
	# Launch in a new namespace
	exec_in_namespace "$@"

	# Prepare the environment
	prepareenv

	print_headline "Toolchain compilation (${BUILD_ARCH})"

	# Build the toolchain
	build_toolchain

	# Ensure the toolchain directory exists
	mkdir -p "${TOOLCHAIN_DIR}"

	# Compress the toolchain
	if ! compress_toolchain "${TOOLCHAIN}"; then
		exiterror "Could not compress toolchain"
	fi
	;;

gettoolchain)
	download_toolchain "${TOOLCHAIN}"
	;;
uploadsrc)
	# Check if IPFIRE_USER is set
	if [ -z "${IPFIRE_USER}" ]; then
		exiterror "You have to setup IPFIRE_USER first. See .config for details."
	fi

	# Sync with upstream
	rsync \
		--recursive \
		--update \
		--ignore-existing \
		--progress \
		--human-readable \
		--exclude="toolchains/" \
		"${CACHE_DIR}/" \
		"${IPFIRE_USER}@people.ipfire.org:/pub/sources/source-2.x"

	exit 0
	;;
lang)
	echo -ne "Checking the translations for missing or obsolete strings..."
	chmod 755 $BASEDIR/tools/{check_strings.pl,sort_strings.pl,check_langs.sh}
	$BASEDIR/tools/sort_strings.pl en
	$BASEDIR/tools/sort_strings.pl de
	$BASEDIR/tools/sort_strings.pl fr
	$BASEDIR/tools/sort_strings.pl es
	$BASEDIR/tools/sort_strings.pl pl
	$BASEDIR/tools/sort_strings.pl ru
	$BASEDIR/tools/sort_strings.pl nl
	$BASEDIR/tools/sort_strings.pl tr
	$BASEDIR/tools/sort_strings.pl it
	$BASEDIR/tools/sort_strings.pl tw
	$BASEDIR/tools/sort_strings.pl zh
	$BASEDIR/tools/check_strings.pl en > $BASEDIR/doc/language_issues.en
	$BASEDIR/tools/check_strings.pl de > $BASEDIR/doc/language_issues.de
	$BASEDIR/tools/check_strings.pl fr > $BASEDIR/doc/language_issues.fr
	$BASEDIR/tools/check_strings.pl es > $BASEDIR/doc/language_issues.es
	$BASEDIR/tools/check_strings.pl pl > $BASEDIR/doc/language_issues.pl
	$BASEDIR/tools/check_strings.pl ru > $BASEDIR/doc/language_issues.ru
	$BASEDIR/tools/check_strings.pl nl > $BASEDIR/doc/language_issues.nl
	$BASEDIR/tools/check_strings.pl tr > $BASEDIR/doc/language_issues.tr
	$BASEDIR/tools/check_strings.pl it > $BASEDIR/doc/language_issues.it
	$BASEDIR/tools/check_strings.pl tw > $BASEDIR/doc/language_issues.tw
	$BASEDIR/tools/check_strings.pl zh > $BASEDIR/doc/language_issues.zh
	$BASEDIR/tools/check_langs.sh > $BASEDIR/doc/language_missings
	print_status DONE

	echo -ne "Updating language lists..."
	update_language_list ${BASEDIR}/src/installer/po
	update_language_list ${BASEDIR}/src/setup/po
	print_status DONE
	;;
update-contributors)
	update_contributors
	;;
find-dependencies)
	shift
	exec "${BASEDIR}/tools/find-dependencies" "${BUILD_DIR}" "$@"
	;;
check-manualpages)
	echo "Checking the manual pages for broken links..."

	chmod 755 $BASEDIR/tools/check_manualpages.pl
	if $BASEDIR/tools/check_manualpages.pl; then
		print_status DONE
	else
		print_status FAIL
	fi
	;;
__timer)
	__timer "${2}" || exit $?
	;;
*)
	echo "Usage: $0 [OPTIONS] {build|check-manualpages|clean|downloadsrc|find-dependencies|gettoolchain|lang|shell|tail|toolchain|update-contributors|uploadsrc}"
	cat doc/make.sh-usage
	;;
esac
