#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2007-2020 IPFire Team <info@ipfire.org>.                   #
#                                                                          #
############################################################################
#

NAME="IPFire"							# Software name
SNAME="ipfire"							# Short name
# If you update the version don't forget to update backupiso and add it to core update
VERSION="2.25"							# Version number
CORE="155"							# Core Level (Filename)
SLOGAN="www.ipfire.org"						# Software slogan
CONFIG_ROOT=/var/ipfire						# Configuration rootdir
MAX_RETRIES=1							# prefetch/check loop
BUILD_IMAGES=1							# Flash and Xen Downloader
KVER=`grep --max-count=1 VER lfs/linux | awk '{ print $3 }'`

# Information from Git
GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"			# Git Branch
GIT_TAG="$(git tag | tail -1)"					# Git Tag
GIT_LASTCOMMIT="$(git rev-parse --verify HEAD)"			# Last commit

TOOLCHAINVER=20200924

###############################################################################
#
# Beautifying variables & presentation & input output interface
#
###############################################################################

# Remember if the shell is interactive or not
if [ -t 0 ] && [ -t 1 ]; then
	INTERACTIVE=true
else
	INTERACTIVE=false
fi

# Sets or adjusts pretty formatting variables
resize_terminal() {
	## Screen Dimentions
	# Find current screen size
	COLUMNS=$(tput cols)

	# When using remote connections, such as a serial port, stty size returns 0
	if ! ${INTERACTIVE} || [ "${COLUMNS}" = "0" ]; then
		COLUMNS=80
	fi

	# Measurements for positioning result messages
	OPTIONS_WIDTH=20
	TIME_WIDTH=12
	STATUS_WIDTH=8
	NAME_WIDTH=$(( COLUMNS - OPTIONS_WIDTH - TIME_WIDTH - STATUS_WIDTH ))
	LINE_WIDTH=$(( COLUMNS - STATUS_WIDTH ))

	TIME_COL=$(( NAME_WIDTH + OPTIONS_WIDTH ))
	STATUS_COL=$(( TIME_COL + TIME_WIDTH ))
}

# Initially setup terminal
resize_terminal

# Call resize_terminal when terminal is being resized
trap "resize_terminal" WINCH

# Define color for messages
BOLD="\\033[1;39m"
DONE="\\033[1;32m"
SKIP="\\033[1;34m"
WARN="\\033[1;35m"
FAIL="\\033[1;31m"
NORMAL="\\033[0;39m"

# New architecture variables
HOST_ARCH="$(uname -m)"

PWD=$(pwd)
BASENAME=$(basename $0)

# Debian specific settings
if [ ! -e /etc/debian_version ]; then
	FULLPATH=`which $0`
else
	if [ -x /usr/bin/realpath ]; then
		FULLPATH=`/usr/bin/realpath $0`
	else
		echo "ERROR: Need to do apt-get install realpath"
		exit 1
	fi
fi

# This is the directory where make.sh is in
export BASEDIR=$(echo $FULLPATH | sed "s/\/$BASENAME//g")

LOGFILE=$BASEDIR/log/_build.preparation.log
export LOGFILE
DIR_CHK=$BASEDIR/cache/check
mkdir $BASEDIR/log/ 2>/dev/null

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

configure_build() {
	local build_arch="${1}"

	if [ "${build_arch}" = "default" ]; then
		build_arch="$(configure_build_guess)"
	fi

	case "${build_arch}" in
		x86_64)
			BUILDTARGET="${build_arch}-unknown-linux-gnu"
			CROSSTARGET="${build_arch}-cross-linux-gnu"
			BUILD_PLATFORM="x86"
			CFLAGS_ARCH="-m64 -mtune=generic -fstack-clash-protection -fcf-protection"
			;;

		i586)
			BUILDTARGET="${build_arch}-pc-linux-gnu"
			CROSSTARGET="${build_arch}-cross-linux-gnu"
			BUILD_PLATFORM="x86"
			CFLAGS_ARCH="-march=i586 -mtune=generic -fomit-frame-pointer"
			;;

		aarch64)
			BUILDTARGET="${build_arch}-unknown-linux-gnu"
			CROSSTARGET="${build_arch}-cross-linux-gnu"
			BUILD_PLATFORM="arm"
			CFLAGS_ARCH="-fstack-clash-protection"
			;;

		armv7hl)
			BUILDTARGET="${build_arch}-unknown-linux-gnueabi"
			CROSSTARGET="${build_arch}-cross-linux-gnueabi"
			BUILD_PLATFORM="arm"
			CFLAGS_ARCH="-march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=hard"
			;;

		armv5tel)
			BUILDTARGET="${build_arch}-unknown-linux-gnueabi"
			CROSSTARGET="${build_arch}-cross-linux-gnueabi"
			BUILD_PLATFORM="arm"
			CFLAGS_ARCH="-march=armv5te -mfloat-abi=soft -fomit-frame-pointer"
			RUSTFLAGS="-Ccodegen-units=1"
			;;

		*)
			exiterror "Cannot build for architure ${build_arch}"
			;;
	esac

	# Check if the QEMU helper is available if needed.
	if qemu_is_required "${build_arch}"; then
		local qemu_build_helper="$(qemu_find_build_helper_name "${build_arch}")"

		if [ -n "${qemu_build_helper}" ]; then
			QEMU_TARGET_HELPER="${qemu_build_helper}"
		else
			exiterror "Could not find a binfmt_misc helper entry for ${build_arch}"
		fi
	fi

	BUILD_ARCH="${build_arch}"
	TOOLS_DIR="/tools_${BUILD_ARCH}"

	# Enables hardening
	HARDENING_CFLAGS="-Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fstack-protector-strong"

	CFLAGS="-O2 -pipe -Wall -fexceptions -fPIC ${CFLAGS_ARCH}"
	CXXFLAGS="${CFLAGS}"

	# Determine parallelism
	# We assume that each process consumes about
	# 128MB of memory. Therefore we find out how
	# many processes fit into memory.
	local mem_max=$(( ${SYSTEM_MEMORY} / 128 ))
	local cpu_max=$(( ${SYSTEM_PROCESSORS} + 1 ))

	local parallelism
	if [ ${mem_max} -lt ${cpu_max} ]; then
		parallelism=${mem_max}
	else
		parallelism=${cpu_max}
	fi

	# Use this as default PARALLELISM
	DEFAULT_PARALLELISM="${parallelism}"

	# Limit lauched ninja build jobs to computed parallel value.
	NINJAJOBS="${parallelism}"

	# Compression parameters
	# We use mode 8 for reasonable memory usage when decompressing
	# but with overall good compression
	XZ_OPT="-8"

	# We try to use as many cores as possible
	XZ_OPT="${XZ_OPT} -T0"

	# We need to limit memory because XZ uses too much when running
	# in parallel and it isn't very smart in limiting itself.
	# We allow XZ to use up to 70% of all system memory.
	local xz_memory=$(( SYSTEM_MEMORY * 7 / 10 ))

	# XZ memory cannot be larger than 2GB on 32 bit systems
	case "${build_arch}" in
		i*86|armv*)
			if [ ${xz_memory} -gt 2048 ]; then
				xz_memory=2048
			fi
			;;
	esac

	XZ_OPT="${XZ_OPT} --memory=${xz_memory}MiB"
}

configure_build_guess() {
	case "${HOST_ARCH}" in
		x86_64)
			echo "x86_64"
			;;
		i?86)
			echo "i586"
			;;

		aarch64)
			echo "aarch64"
			;;

		armv7*|armv6*|armv5*)
			echo "armv5tel"
			;;

		*)
			exiterror "Cannot guess build architecture"
			;;
	esac
}

stdumount() {
	umount $BASEDIR/build/sys			2>/dev/null;
	umount $BASEDIR/build/dev/shm		2>/dev/null;
	umount $BASEDIR/build/dev/pts		2>/dev/null;
	umount $BASEDIR/build/dev			2>/dev/null;
	umount $BASEDIR/build/proc			2>/dev/null;
	umount $BASEDIR/build/install/mnt		2>/dev/null;
	umount $BASEDIR/build/usr/src/cache	2>/dev/null;
	umount $BASEDIR/build/usr/src/ccache	2>/dev/null;
	umount $BASEDIR/build/usr/src/config	2>/dev/null;
	umount $BASEDIR/build/usr/src/doc		2>/dev/null;
	umount $BASEDIR/build/usr/src/html		2>/dev/null;
	umount $BASEDIR/build/usr/src/langs	2>/dev/null;
	umount $BASEDIR/build/usr/src/lfs		2>/dev/null;
	umount $BASEDIR/build/usr/src/log		2>/dev/null;
	umount $BASEDIR/build/usr/src/src		2>/dev/null;
	umount $BASEDIR/build/usr/src		2>/dev/null;
	umount $BASEDIR/build/tmp		2>/dev/null;
}

now() {
	date -u "+%s"
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
	local line="$@"

	printf "%-${LINE_WIDTH}s" "${line}"
}

_print_line() {
	local status="${1}"
	shift

	if ${INTERACTIVE}; then
		printf "${!status}"
	fi

	print_line "$@"

	if ${INTERACTIVE}; then
		printf "${NORMAL}"
	fi
}

print_headline() {
	_print_line BOLD "$@"
}

print_error() {
	_print_line FAIL "$@"
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

	printf "%-$(( ${NAME_WIDTH} - 1 ))s " "${string}"
	printf "%$(( ${OPTIONS_WIDTH} - 1 ))s " "${options}"
}

print_runtime() {
	local runtime=$(format_runtime $@)

	if ${INTERACTIVE}; then
		printf "\\033[${TIME_COL}G[ ${BOLD}%$(( ${TIME_WIDTH} - 4 ))s${NORMAL} ]" "${runtime}"
	else
		printf "[ %$(( ${TIME_WIDTH} - 4 ))s ]" "${runtime}"
	fi
}

print_status() {
	local status="${1}"

	local color="${!status}"

	if ${INTERACTIVE}; then
		printf "\\033[${STATUS_COL}G[${color-${BOLD}} %-$(( ${STATUS_WIDTH} - 4 ))s ${NORMAL}]\n" "${status}"
	else
		printf "[ %-$(( ${STATUS_WIDTH} - 4 ))s ]\n" "${status}"
	fi
}

print_build_stage() {
	print_headline "$@"

	# end line
	printf "\n"
}

print_build_summary() {
	local runtime=$(format_runtime $@)

	print_line "*** Build finished in ${runtime}"
	print_status DONE
}

exiterror() {
	stdumount
	for i in `seq 0 7`; do
		if ( losetup /dev/loop${i} 2>/dev/null | grep -q "/install/images" ); then
		losetup -d /dev/loop${i} 2>/dev/null
		fi;
	done

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
		print_error "${line}"
		print_status FAIL
	done

	exit 1
}

prepareenv() {
	# Are we running the right shell?
	if [ -z "${BASH}" ]; then
		exiterror "BASH environment variable is not set.  You're probably running the wrong shell."
	fi

	if [ -z "${BASH_VERSION}" ]; then
		exiterror "Not running BASH shell."
	fi

	# Trap on emergency exit
	trap "exiterror 'Build process interrupted'" SIGINT SIGTERM SIGKILL SIGSTOP SIGQUIT

	# Checking if running as root user
	if [ $(id -u) -ne 0 ]; then
			exiterror "root privileges required for building"
	fi

	# Checking for necessary temporary space
	print_line "Checking for necessary space on disk $BASE_DEV"
	BASE_DEV=`df -P -k $BASEDIR | tail -n 1 | awk '{ print $1 }'`
	BASE_ASPACE=`df -P -k $BASEDIR | tail -n 1 | awk '{ print $4 }'`
	if (( 2048000 > $BASE_ASPACE )); then
			BASE_USPACE=`du -skx $BASEDIR | awk '{print $1}'`
			if (( 2048000 - $BASE_USPACE > $BASE_ASPACE )); then
				print_status FAIL
				exiterror "Not enough temporary space available, need at least 2GB on $BASE_DEV"
			fi
	else
			print_status DONE
	fi

	# Set umask
	umask 022

	# Set LFS Directory
	LFS=$BASEDIR/build

	# Setup environment
	set +h
	LC_ALL=POSIX
	export LFS LC_ALL CFLAGS CXXFLAGS DEFAULT_PARALLELISM RUSTFLAGS NINJAJOBS
	unset CC CXX CPP LD_LIBRARY_PATH LD_PRELOAD

	# Make some extra directories
	mkdir -p "${BASEDIR}/build${TOOLS_DIR}" 2>/dev/null
	mkdir -p $BASEDIR/build/{etc,usr/src} 2>/dev/null
	mkdir -p $BASEDIR/build/{dev/{shm,pts},proc,sys}
	mkdir -p $BASEDIR/{cache,ccache/${BUILD_ARCH}} 2>/dev/null

	if [ "${ENABLE_RAMDISK}" = "on" ]; then
		mkdir -p $BASEDIR/build/usr/src
		mount -t tmpfs tmpfs -o size=8G,nr_inodes=1M,mode=1777 $BASEDIR/build/usr/src

		mkdir -p ${BASEDIR}/build/tmp
		mount -t tmpfs tmpfs -o size=4G,nr_inodes=1M,mode=1777 ${BASEDIR}/build/tmp
	fi

	mkdir -p $BASEDIR/build/usr/src/{cache,config,doc,html,langs,lfs,log,src,ccache}

	mknod -m 600 $BASEDIR/build/dev/console c 5 1 2>/dev/null
	mknod -m 666 $BASEDIR/build/dev/null c 1 3 2>/dev/null

	# Make all sources and proc available under lfs build
	mount --bind /dev            $BASEDIR/build/dev
	mount --bind /dev/pts        $BASEDIR/build/dev/pts
	mount --bind /dev/shm        $BASEDIR/build/dev/shm
	mount --bind /proc           $BASEDIR/build/proc
	mount --bind /sys            $BASEDIR/build/sys
	mount --bind $BASEDIR/cache  $BASEDIR/build/usr/src/cache
	mount --bind $BASEDIR/ccache/${BUILD_ARCH} $BASEDIR/build/usr/src/ccache
	mount --bind $BASEDIR/config $BASEDIR/build/usr/src/config
	mount --bind $BASEDIR/doc    $BASEDIR/build/usr/src/doc
	mount --bind $BASEDIR/html   $BASEDIR/build/usr/src/html
	mount --bind $BASEDIR/langs  $BASEDIR/build/usr/src/langs
	mount --bind $BASEDIR/lfs    $BASEDIR/build/usr/src/lfs
	mount --bind $BASEDIR/log    $BASEDIR/build/usr/src/log
	mount --bind $BASEDIR/src    $BASEDIR/build/usr/src/src

	# Run LFS static binary creation scripts one by one
	export CCACHE_DIR=$BASEDIR/ccache
	export CCACHE_TEMPDIR="/tmp"
	export CCACHE_COMPRESS=1
	export CCACHE_COMPILERCHECK="string:toolchain-${TOOLCHAINVER} ${BUILD_ARCH}"

	# Remove pre-install list of installed files in case user erase some files before rebuild
	rm -f $BASEDIR/build/usr/src/lsalr 2>/dev/null

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
	enterchroot ccache --max-size="${CCACHE_CACHE_SIZE}" >/dev/null
}

enterchroot() {
	# Install QEMU helper, if needed
	qemu_install_helper

	local PATH="${TOOLS_DIR}/ccache/bin:/bin:/usr/bin:/sbin:/usr/sbin:${TOOLS_DIR}/bin"

	PATH="${PATH}" chroot ${LFS} env -i \
		HOME="/root" \
		TERM="${TERM}" \
		PS1="${PS1}" \
		PATH="${PATH}" \
		SYSTEM_RELEASE="${SYSTEM_RELEASE}" \
		PAKFIRE_TREE="${PAKFIRE_TREE}" \
		NAME="${NAME}" \
		SNAME="${SNAME}" \
		VERSION="${VERSION}" \
		CORE="${CORE}" \
		SLOGAN="${SLOGAN}" \
		TOOLS_DIR="${TOOLS_DIR}" \
		CONFIG_ROOT="${CONFIG_ROOT}" \
		CFLAGS="${CFLAGS} ${HARDENING_CFLAGS}" \
		CXXFLAGS="${CXXFLAGS} ${HARDENING_CFLAGS}" \
		RUSTFLAGS="${RUSTFLAGS}" \
		BUILDTARGET="${BUILDTARGET}" \
		CROSSTARGET="${CROSSTARGET}" \
		BUILD_ARCH="${BUILD_ARCH}" \
		BUILD_PLATFORM="${BUILD_PLATFORM}" \
		CCACHE_DIR=/usr/src/ccache \
		CCACHE_TEMPDIR="${CCACHE_TEMPDIR}" \
		CCACHE_COMPRESS="${CCACHE_COMPRESS}" \
		CCACHE_COMPILERCHECK="${CCACHE_COMPILERCHECK}" \
		GOCACHE="/usr/src/ccache/go" \
		KVER="${KVER}" \
		XZ_OPT="${XZ_OPT}" \
		DEFAULT_PARALLELISM="${DEFAULT_PARALLELISM}" \
		SYSTEM_PROCESSORS="${SYSTEM_PROCESSORS}" \
		SYSTEM_MEMORY="${SYSTEM_MEMORY}" \
		$(fake_environ) \
		$(qemu_environ) \
		"$@"
}

entershell() {
	if [ ! -e $BASEDIR/build/usr/src/lfs/ ]; then
		exiterror "No such file or directory: $BASEDIR/build/usr/src/lfs/"
	fi

	echo "Entering to a shell inside LFS chroot, go out with exit"
	local PS1="ipfire build chroot (${BUILD_ARCH}) \u:\w\$ "

	if enterchroot bash -i; then
		stdumount
	else
		print_status FAIL
		exiterror "chroot error"
	fi
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

	# Script slipped?
	local i
	for i in $SKIP_PACKAGE_LIST
	do
		if [ "$i" == "$1" ]; then
			print_status SKIP
			return 1;
		fi
	done

	echo -ne "`date -u '+%b %e %T'`: Building $* " >> $LOGFILE

	cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR BUILD_ARCH="${BUILD_ARCH}" \
		MESSAGE="$1\t " download  >> $LOGFILE 2>&1
	if [ $? -ne 0 ]; then
		exiterror "Download error in $1"
	fi

	cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR BUILD_ARCH="${BUILD_ARCH}" \
		MESSAGE="$1\t md5sum" md5  >> $LOGFILE 2>&1
	if [ $? -ne 0 ]; then
		exiterror "md5sum error in $1, check file in cache or signature"
	fi

	return 0	# pass all!
}

lfsmake1() {
	lfsmakecommoncheck $*
	[ $? == 1 ] && return 0

	cd $BASEDIR/lfs && env -i \
		PATH="${TOOLS_DIR}/ccache/bin:${TOOLS_DIR}/bin:$PATH" \
		CCACHE_DIR="${CCACHE_DIR}" \
		CCACHE_TEMPDIR="${CCACHE_TEMPDIR}" \
		CCACHE_COMPRESS="${CCACHE_COMPRESS}" \
		CCACHE_COMPILERCHECK="${CCACHE_COMPILERCHECK}" \
		CFLAGS="${CFLAGS}" \
		CXXFLAGS="${CXXFLAGS}" \
		DEFAULT_PARALLELISM="${DEFAULT_PARALLELISM}" \
		SYSTEM_PROCESSORS="${SYSTEM_PROCESSORS}" \
		SYSTEM_MEMORY="${SYSTEM_MEMORY}" \
		make -f $* \
			TOOLCHAIN=1 \
			TOOLS_DIR="${TOOLS_DIR}" \
			CROSSTARGET="${CROSSTARGET}" \
			BUILDTARGET="${BUILDTARGET}" \
			BUILD_ARCH="${BUILD_ARCH}" \
			BUILD_PLATFORM="${BUILD_PLATFORM}" \
			LFS_BASEDIR="${BASEDIR}" \
			ROOT="${LFS}" \
			KVER="${KVER}" \
			install >> $LOGFILE 2>&1 &

	if ! wait_until_finished $!; then
		print_status FAIL
		exiterror "Building $*"
	fi

	print_status DONE
}

lfsmake2() {
	lfsmakecommoncheck $*
	[ $? == 1 ] && return 0

	local PS1='\u:\w$ '

	enterchroot \
		${EXTRA_PATH}bash -x -c "cd /usr/src/lfs && \
			make -f $* \
			LFS_BASEDIR=/usr/src install" \
		>> ${LOGFILE} 2>&1 &

	if ! wait_until_finished $!; then
		print_status FAIL
		exiterror "Building $*"
	fi

	print_status DONE
}

ipfiredist() {
	lfsmakecommoncheck $*
	[ $? == 1 ] && return 0

	local PS1='\u:\w$ '

	enterchroot \
		bash -x -c "cd /usr/src/lfs && make -f $* LFS_BASEDIR=/usr/src dist" \
		>> ${LOGFILE} 2>&1 &

	if ! wait_until_finished $!; then
		print_status FAIL
		exiterror "Packaging $*"
	fi

	print_status DONE
}

wait_until_finished() {
	local pid=${1}

	local start_time=$(now)

	# Show progress
	if ${INTERACTIVE}; then
		# Wait a little just in case the process
		# has finished very quickly.
		sleep 0.1

		local runtime
		while kill -0 ${pid} 2>/dev/null; do
			print_runtime $(( $(now) - ${start_time} ))

			# Wait a little
			sleep 1
		done
	fi

	# Returns the exit code of the child process
	wait ${pid}
	local ret=$?

	if ! ${INTERACTIVE}; then
		print_runtime $(( $(now) - ${start_time} ))
	fi

	return ${ret}
}

fake_environ() {
	[ -e "${BASEDIR}/build${TOOLS_DIR}/lib/libpakfire_preload.so" ] || return

	local env="LD_PRELOAD=${TOOLS_DIR}/lib/libpakfire_preload.so"

	# Fake kernel version, because some of the packages do not compile
	# with kernel 3.0 and later.
	env="${env} UTS_RELEASE=${KVER}-ipfire"

	# Fake machine version.
	env="${env} UTS_MACHINE=${BUILD_ARCH}"

	echo "${env}"
}

qemu_environ() {
	local env

	# Don't add anything if qemu is not used.
	if ! qemu_is_required; then
		return
	fi

	# Set default qemu options
	case "${BUILD_ARCH}" in
		arm*)
			QEMU_CPU="${QEMU_CPU:-cortex-a9}"

			env="${env} QEMU_CPU=${QEMU_CPU}"
			;;
	esac

	# Enable QEMU strace
	#env="${env} QEMU_STRACE=1"

	echo "${env}"
}

qemu_is_required() {
	local build_arch="${1}"

	if [ -z "${build_arch}" ]; then
		build_arch="${BUILD_ARCH}"
	fi

	case "${HOST_ARCH},${build_arch}" in
		x86_64,arm*|x86_64,aarch64|i?86,arm*|i?86,aarch64|i?86,x86_64)
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


	if [ -z "${QEMU_TARGET_HELPER}" ]; then
		exiterror "QEMU_TARGET_HELPER not set"
	fi

	# Check if the helper is already installed.
	if [ -x "${LFS}${QEMU_TARGET_HELPER}" ]; then
		return 0
	fi

	# Try to find a suitable binary that we can install
	# to the build environment.
	local file
	for file in "${QEMU_TARGET_HELPER}" "${QEMU_TARGET_HELPER}-static"; do
		# file must exist and be executable.
		[ -x "${file}" ] || continue

		# Must be static.
		file_is_static "${file}" || continue

		local dirname="${LFS}$(dirname "${file}")"
		mkdir -p "${dirname}"

		install -m 755 "${file}" "${LFS}${QEMU_TARGET_HELPER}"
		return 0
	done

	exiterror "Could not find a statically-linked QEMU emulator: ${QEMU_TARGET_HELPER}"
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

	file ${file} 2>/dev/null | grep -q "statically linked"
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

# Default settings
CCACHE_CACHE_SIZE="4G"
ENABLE_RAMDISK="auto"

# Load configuration file
if [ -f .config ]; then
	. .config
fi

# TARGET_ARCH is BUILD_ARCH now
if [ -n "${TARGET_ARCH}" ]; then
	BUILD_ARCH="${TARGET_ARCH}"
	unset TARGET_ARCH
fi

# Get some information about the host system
SYSTEM_PROCESSORS="$(system_processors)"
SYSTEM_MEMORY="$(system_memory)"

if [ -n "${BUILD_ARCH}" ]; then
	configure_build "${BUILD_ARCH}"
else
	configure_build "default"
fi

# Automatically enable/disable ramdisk usage
if [ "${ENABLE_RAMDISK}" = "auto" ]; then
	# Enable only when the host system has 4GB of RAM or more
	if [ ${SYSTEM_MEMORY} -ge 3900 ]; then
		ENABLE_RAMDISK="on"
	fi
fi

buildtoolchain() {
	local error=false
	case "${BUILD_ARCH}:${HOST_ARCH}" in
		# x86_64
		x86_64:x86_64)
			 # This is working.
			 ;;

		# x86
		i586:i586|i586:i686|i586:x86_64)
			# These are working.
			;;
		i586:*)
			error=true
			;;

		# ARM
		arvm7hl:armv7hl|armv7hl:armv7l)
			# These are working.
			;;

		armv5tel:armv5tel|armv5tel:armv5tejl|armv5tel:armv6l|armv5tel:armv7l|armv5tel:aarch64)
			# These are working.
			;;
		armv5tel:*)
			error=true
			;;
	esac

	${error} && \
		exiterror "Cannot build ${BUILD_ARCH} toolchain on $(uname -m). Please use the download if any."

	local gcc=$(type -p gcc)
	if [ -z "${gcc}" ]; then
		exiterror "Could not find GCC. You will need a working build enviroment in order to build the toolchain."
	fi

	# Check ${TOOLS_DIR} symlink
	if [ -h "${TOOLS_DIR}" ]; then
		rm -f "${TOOLS_DIR}"
	fi

	if [ ! -e "${TOOLS_DIR}" ]; then
		ln -s "${BASEDIR}/build${TOOLS_DIR}" "${TOOLS_DIR}"
	fi

	if [ ! -h "${TOOLS_DIR}" ]; then
		exiterror "Could not create ${TOOLS_DIR} symbolic link"
	fi

	LOGFILE="$BASEDIR/log/_build.toolchain.log"
	export LOGFILE

	lfsmake1 stage1
	lfsmake1 ccache			PASS=1
	lfsmake1 binutils			PASS=1
	lfsmake1 gcc			PASS=1
	lfsmake1 linux			KCFG="-headers"
	lfsmake1 glibc
	lfsmake1 libxcrypt
	lfsmake1 gcc			PASS=L
	lfsmake1 binutils			PASS=2
	lfsmake1 gcc			PASS=2
	lfsmake1 zlib
	lfsmake1 ccache			PASS=2
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
	lfsmake1 strip
	lfsmake1 cleanup-toolchain
}

buildbase() {
	LOGFILE="$BASEDIR/log/_build.base.log"
	export LOGFILE
	lfsmake2 stage2
	lfsmake2 linux			KCFG="-headers"
	lfsmake2 man-pages
	lfsmake2 glibc
	lfsmake2 tzdata
	lfsmake2 cleanup-toolchain
	lfsmake2 zlib
	lfsmake2 zstd
	lfsmake2 autoconf
	lfsmake2 automake
	lfsmake2 libtool
	lfsmake2 binutils
	lfsmake2 gmp
	lfsmake2 mpfr
	lfsmake2 libmpc
	lfsmake2 libxcrypt
	lfsmake2 file
	lfsmake2 gcc
	lfsmake2 sed
	lfsmake2 berkeley
	lfsmake2 berkeley-compat
	lfsmake2 coreutils
	lfsmake2 iana-etc
	lfsmake2 m4
	lfsmake2 bison
	lfsmake2 ncurses
	lfsmake2 perl
	lfsmake2 readline
	lfsmake2 readline-compat
	lfsmake2 bzip2
	lfsmake2 xz
	lfsmake2 lzip
	lfsmake2 pcre
	lfsmake2 pcre2
	lfsmake2 gettext
	lfsmake2 attr
	lfsmake2 acl
	lfsmake2 bash
	lfsmake2 diffutils
	lfsmake2 e2fsprogs
	lfsmake2 ed
	lfsmake2 findutils
	lfsmake2 flex
	lfsmake2 gawk
	lfsmake2 go
	lfsmake2 grep
	lfsmake2 groff
	lfsmake2 gperf
	lfsmake2 gzip
	lfsmake2 hostname
	lfsmake2 iproute2
	lfsmake2 jwhois
	lfsmake2 kbd
	lfsmake2 less
	lfsmake2 pkg-config
	lfsmake2 procps
	lfsmake2 make
	lfsmake2 man
	lfsmake2 net-tools
	lfsmake2 patch
	lfsmake2 psmisc
	lfsmake2 shadow
	lfsmake2 sysklogd
	lfsmake2 sysvinit
	lfsmake2 tar
	lfsmake2 texinfo
	lfsmake2 util-linux
	lfsmake2 vim
}

buildipfire() {
  LOGFILE="$BASEDIR/log/_build.ipfire.log"
  export LOGFILE
  lfsmake2 configroot
  lfsmake2 initscripts
  lfsmake2 backup
  lfsmake2 openssl
  lfsmake2 kmod
  lfsmake2 udev
  lfsmake2 popt
  lfsmake2 libedit
  lfsmake2 libusb
  lfsmake2 libusb-compat
  lfsmake2 libpcap
  lfsmake2 ppp
  lfsmake2 pptp
  lfsmake2 unzip
  lfsmake2 which
  lfsmake2 linux-firmware
  lfsmake2 dvb-firmwares
  lfsmake2 xr819-firmware
  lfsmake2 zd1211-firmware
  lfsmake2 rpi-firmware
  lfsmake2 intel-microcode
  lfsmake2 pcengines-apu-firmware
  lfsmake2 bc
  lfsmake2 u-boot MKIMAGE=1
  lfsmake2 cpio
  lfsmake2 mdadm
  lfsmake2 dracut
  lfsmake2 libaio
  lfsmake2 lvm2
  lfsmake2 multipath-tools
  lfsmake2 freetype
  lfsmake2 libmnl
  lfsmake2 libnfnetlink
  lfsmake2 libnetfilter_queue
  lfsmake2 libnetfilter_conntrack
  lfsmake2 libnetfilter_cthelper
  lfsmake2 libnetfilter_cttimeout
  lfsmake2 iptables
  lfsmake2 screen
  lfsmake2 elfutils

  case "${BUILD_ARCH}" in
	x86_64|aarch64)
		lfsmake2 linux			KCFG=""
#		lfsmake2 backports			KCFG=""
#		lfsmake2 e1000e			KCFG=""
#		lfsmake2 igb				KCFG=""
#		lfsmake2 ixgbe			KCFG=""
		lfsmake2 xtables-addons		KCFG=""
		lfsmake2 linux-initrd			KCFG=""
		;;
	i586)
		# x86 kernel build
		lfsmake2 linux			KCFG=""
#		lfsmake2 backports			KCFG=""
#		lfsmake2 e1000e			KCFG=""
#		lfsmake2 igb				KCFG=""
#		lfsmake2 ixgbe			KCFG=""
		lfsmake2 xtables-addons		KCFG=""
		lfsmake2 linux-initrd			KCFG=""
		;;

	armv5tel)
		# arm multi platform (Panda, Wandboard ...) kernel build
		lfsmake2 linux			KCFG="-multi"
#		lfsmake2 backports			KCFG="-multi"
#		lfsmake2 e1000e			KCFG="-multi"
#		lfsmake2 igb				KCFG="-multi"
#		lfsmake2 ixgbe			KCFG="-multi"
		lfsmake2 xtables-addons		KCFG="-multi"
		lfsmake2 linux-initrd			KCFG="-multi"
		;;
  esac
  lfsmake2 xtables-addons			USPACE="1"
  lfsmake2 libgpg-error
  lfsmake2 libgcrypt
  lfsmake2 libassuan
  lfsmake2 nettle
  lfsmake2 json-c
  lfsmake2 libconfig
  lfsmake2 libevent
  lfsmake2 libevent2
  lfsmake2 expat
  lfsmake2 apr
  lfsmake2 aprutil
  lfsmake2 unbound
  lfsmake2 gnutls
  lfsmake2 bind
  lfsmake2 dhcp
  lfsmake2 dhcpcd
  lfsmake2 boost
  lfsmake2 linux-atm
  lfsmake2 gdbm
  lfsmake2 pam
  lfsmake2 c-ares
  lfsmake2 curl
  lfsmake2 tcl
  lfsmake2 sqlite
  lfsmake2 libffi
  lfsmake2 python
  lfsmake2 python3
  lfsmake2 gdb
  lfsmake2 grub
  lfsmake2 efivar
  lfsmake2 efibootmgr
  lfsmake2 ca-certificates
  lfsmake2 fireinfo
  lfsmake2 libnet
  lfsmake2 libnl
  lfsmake2 libnl-3
  lfsmake2 libidn
  lfsmake2 nasm
  lfsmake2 libarchive
  lfsmake2 cmake
  lfsmake2 ninja
  lfsmake2 meson
  lfsmake2 libjpeg
  lfsmake2 libjpeg-compat
  lfsmake2 openjpeg
  lfsmake2 libexif
  lfsmake2 libpng
  lfsmake2 libtiff
  lfsmake2 libart
  lfsmake2 gd
  lfsmake2 slang
  lfsmake2 newt
  lfsmake2 libsmooth
  lfsmake2 libcap
  lfsmake2 libcap-ng
  lfsmake2 pciutils
  lfsmake2 usbutils
  lfsmake2 libxml2
  lfsmake2 libxslt
  lfsmake2 BerkeleyDB
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
  lfsmake2 cdrkit
  lfsmake2 dosfstools
  lfsmake2 reiserfsprogs
  lfsmake2 xfsprogs
  lfsmake2 sysfsutils
  lfsmake2 fuse
  lfsmake2 ntfs-3g
  lfsmake2 ethtool
  lfsmake2 fcron
  lfsmake2 perl-GD
  lfsmake2 GD-Graph
  lfsmake2 GD-TextUtil
  lfsmake2 perl-Device-SerialPort
  lfsmake2 perl-Device-Modem
  lfsmake2 perl-Apache-Htpasswd
  lfsmake2 perl-Parse-Yapp
  lfsmake2 gnupg
  lfsmake2 hdparm
  lfsmake2 sdparm
  lfsmake2 mtools
  lfsmake2 whatmask
  lfsmake2 libtirpc
  lfsmake2 conntrack-tools
  lfsmake2 libupnp
  lfsmake2 ipaddr
  lfsmake2 iputils
  lfsmake2 l7-protocols
  lfsmake2 hwdata
  lfsmake2 logrotate
  lfsmake2 logwatch
  lfsmake2 misc-progs
  lfsmake2 nano
  lfsmake2 URI
  lfsmake2 perl-CGI
  lfsmake2 perl-Switch
  lfsmake2 HTML-Tagset
  lfsmake2 HTML-Parser
  lfsmake2 HTML-Template
  lfsmake2 Compress-Zlib
  lfsmake2 Digest
  lfsmake2 Digest-SHA1
  lfsmake2 Digest-HMAC
  lfsmake2 libwww-perl
  lfsmake2 Net-DNS
  lfsmake2 Net-IPv4Addr
  lfsmake2 Net_SSLeay
  lfsmake2 IO-Stringy
  lfsmake2 IO-Socket-SSL
  lfsmake2 Unix-Syslog
  lfsmake2 Mail-Tools
  lfsmake2 MIME-Tools
  lfsmake2 Net-Server
  lfsmake2 Convert-TNEF
  lfsmake2 Convert-UUlib
  lfsmake2 Archive-Tar
  lfsmake2 Archive-Zip
  lfsmake2 Text-Tabs+Wrap
  lfsmake2 XML-Parser
  lfsmake2 Crypt-PasswdMD5
  lfsmake2 Net-Telnet
  lfsmake2 python-setuptools
  lfsmake2 python-clientform
  lfsmake2 python-mechanize
  lfsmake2 python-feedparser
  lfsmake2 python-rssdler
  lfsmake2 python-inotify
  lfsmake2 python-docutils
  lfsmake2 python-daemon
  lfsmake2 python-ipaddress
  lfsmake2 glib
  lfsmake2 ntp
  lfsmake2 openssh
  lfsmake2 fontconfig
  lfsmake2 dejavu-fonts-ttf
  lfsmake2 ubuntu-font-family
  lfsmake2 freefont
  lfsmake2 pixman
  lfsmake2 cairo
  lfsmake2 pango
  lfsmake2 rrdtool
  lfsmake2 setup
  lfsmake2 libdnet
  lfsmake2 rust
  lfsmake2 jansson
  lfsmake2 yaml
  lfsmake2 libhtp
  lfsmake2 colm
  lfsmake2 ragel
  lfsmake2 hyperscan
  lfsmake2 suricata
  lfsmake2 oinkmaster
  lfsmake2 ids-ruleset-sources
  lfsmake2 squid
  lfsmake2 squidguard
  lfsmake2 calamaris
  lfsmake2 tcpdump
  lfsmake2 traceroute
  lfsmake2 vlan
  lfsmake2 wireless
  lfsmake2 pakfire
  lfsmake2 spandsp
  lfsmake2 lz4
  lfsmake2 lzo
  lfsmake2 openvpn
  lfsmake2 mpage
  lfsmake2 dbus
  lfsmake2 intltool
  lfsmake2 libdaemon
  lfsmake2 avahi
  lfsmake2 cups
  lfsmake2 lcms2
  lfsmake2 ghostscript
  lfsmake2 qpdf
  lfsmake2 poppler
  lfsmake2 poppler-data
  lfsmake2 cups-filters
  lfsmake2 epson-inkjet-printer-escpr
  lfsmake2 foomatic
  lfsmake2 hplip
  lfsmake2 cifs-utils
  lfsmake2 krb5
  lfsmake2 rpcsvc-proto
  lfsmake2 samba
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
  lfsmake2 mpfire
  lfsmake2 guardian
  lfsmake2 libid3tag
  lfsmake2 libmad
  lfsmake2 libogg
  lfsmake2 libvorbis
  lfsmake2 libdvbpsi
  lfsmake2 flac
  lfsmake2 lame
  lfsmake2 sox
  lfsmake2 soxr
  lfsmake2 libshout
  lfsmake2 xvid
  lfsmake2 libmpeg2
  lfsmake2 gnump3d
  lfsmake2 rsync
  lfsmake2 rpcbind
  lfsmake2 keyutils
  lfsmake2 libnfsidmap
  lfsmake2 nfs
  lfsmake2 gnu-netcat
  lfsmake2 ncat
  lfsmake2 nmap
  lfsmake2 etherwake
  lfsmake2 bwm-ng
  lfsmake2 sysstat
  lfsmake2 strongswan
  lfsmake2 rng-tools
  lfsmake2 lsof
  lfsmake2 br2684ctl
  lfsmake2 pcmciautils
  lfsmake2 lm_sensors
  lfsmake2 liboping
  lfsmake2 collectd
  lfsmake2 elinks
  lfsmake2 igmpproxy
  lfsmake2 fbset
  lfsmake2 opus
  lfsmake2 python-six
  lfsmake2 python-pyparsing
  lfsmake2 spice-protocol
  lfsmake2 spice
  lfsmake2 sdl
  lfsmake2 libusbredir
  lfsmake2 libseccomp
  lfsmake2 qemu
  lfsmake2 sane
  lfsmake2 netpbm
  lfsmake2 netsnmpd
  lfsmake2 nagios_nrpe
  lfsmake2 nagios-plugins
  lfsmake2 icinga
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
  lfsmake2 mpd
  lfsmake2 libmpdclient
  lfsmake2 mpc
  lfsmake2 perl-Net-CIDR-Lite
  lfsmake2 perl-Net-SMTP-SSL
  lfsmake2 perl-MIME-Base64
  lfsmake2 perl-Authen-SASL
  lfsmake2 perl-MIME-Lite
  lfsmake2 perl-Email-Date-Format
  lfsmake2 git
  lfsmake2 squidclamav
  lfsmake2 vnstat
  lfsmake2 iw
  lfsmake2 wpa_supplicant
  lfsmake2 hostapd
  lfsmake2 pycurl
  lfsmake2 urlgrabber
  lfsmake2 syslinux
  lfsmake2 tftpd
  lfsmake2 cpufrequtils
  lfsmake2 gutenprint
  lfsmake2 apcupsd
  lfsmake2 fireperf
  lfsmake2 iperf
  lfsmake2 iperf3
  lfsmake2 7zip
  lfsmake2 lynis
  lfsmake2 sshfs
  lfsmake2 taglib
  lfsmake2 sslh
  lfsmake2 perl-gettext
  lfsmake2 perl-Sort-Naturally
  lfsmake2 vdradmin
  lfsmake2 perl-DBI
  lfsmake2 perl-DBD-SQLite
  lfsmake2 perl-File-ReadBackwards
  lfsmake2 openvmtools
  lfsmake2 libmicrohttpd
  lfsmake2 motion
  lfsmake2 joe
  lfsmake2 monit
  lfsmake2 nut
  lfsmake2 watchdog
  lfsmake2 libpri
  lfsmake2 libsrtp
  lfsmake2 asterisk
  lfsmake2 usb_modeswitch
  lfsmake2 usb_modeswitch_data
  lfsmake2 zerofree
  lfsmake2 minicom
  lfsmake2 ddrescue
  lfsmake2 miniupnpd
  lfsmake2 client175
  lfsmake2 powertop
  lfsmake2 parted
  lfsmake2 swig
  lfsmake2 u-boot
  lfsmake2 u-boot-friendlyarm
  lfsmake2 python-typing
  lfsmake2 python-m2crypto
  lfsmake2 wireless-regdb
  lfsmake2 crda
  lfsmake2 libsolv
  lfsmake2 python-distutils-extra
  lfsmake2 python-lzma
  lfsmake2 python-progressbar
  lfsmake2 ddns
  lfsmake2 python3-setuptools
  lfsmake2 python3-setuptools-scm
  lfsmake2 python3-six
  lfsmake2 python3-dateutil
  lfsmake2 python3-jmespath
  lfsmake2 python3-colorama
  lfsmake2 python3-docutils
  lfsmake2 python3-yaml
  lfsmake2 python3-s3transfer
  lfsmake2 python3-rsa
  lfsmake2 python3-pyasn1
  lfsmake2 python3-urllib3
  lfsmake2 python3-botocore
  lfsmake2 python3-llfuse
  lfsmake2 python3-msgpack
  lfsmake2 aws-cli
  lfsmake2 transmission
  lfsmake2 dpfhack
  lfsmake2 lcd4linux
  lfsmake2 mtr
  lfsmake2 minidlna
  lfsmake2 acpid
  lfsmake2 fping
  lfsmake2 telnet
  lfsmake2 xinetd
  lfsmake2 gpgme
  lfsmake2 pygpgme
  lfsmake2 pakfire3
  lfsmake2 stress
  lfsmake2 libstatgrab
  lfsmake2 sarg
  lfsmake2 nginx
  lfsmake2 sendEmail
  lfsmake2 sysbench
  lfsmake2 strace
  lfsmake2 ltrace
  lfsmake2 ipfire-netboot
  lfsmake2 lcdproc
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
  lfsmake2 squid-accounting
  lfsmake2 pigz
  lfsmake2 tmux
  lfsmake2 perl-Text-CSV_XS
  lfsmake2 lua
  lfsmake2 haproxy
  lfsmake2 ipset
  lfsmake2 dnsdist
  lfsmake2 bird
  lfsmake2 frr
  lfsmake2 dmidecode
  lfsmake2 mcelog
  lfsmake2 util-macros
  lfsmake2 libpciaccess
  lfsmake2 libyajl
  lfsmake2 libvirt
  lfsmake2 libtalloc
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
  lfsmake2 shairport-sync
  lfsmake2 borgbackup
  lfsmake2 lmdb
  lfsmake2 knot
  lfsmake2 spectre-meltdown-checker
  lfsmake2 zabbix_agentd
  lfsmake2 flashrom
  lfsmake2 firmware-update
  lfsmake2 tshark
  lfsmake2 speedtest-cli
  lfsmake2 rfkill
  lfsmake2 amazon-ssm-agent
  lfsmake2 libloc
  lfsmake2 ncdu
  lfsmake2 lshw
  lfsmake2 socat
}

buildinstaller() {
  # Run installer scripts one by one
  LOGFILE="$BASEDIR/log/_build.installer.log"
  export LOGFILE
  lfsmake2 memtest
  lfsmake2 installer
  # use toolchain bash for chroot to strip
  EXTRA_PATH=${TOOLS_DIR}/bin/ lfsmake2 strip
}

buildpackages() {
  LOGFILE="$BASEDIR/log/_build.packages.log"
  export LOGFILE
  echo "... see detailed log in _build.*.log files" >> $LOGFILE

  
  # Generating list of packages used
  print_line "Generating packages list from logs"
  rm -f $BASEDIR/doc/packages-list
  for i in `ls -1tr $BASEDIR/log/[^_]*`; do
	if [ "$i" != "$BASEDIR/log/FILES" -a -n $i ]; then
		echo "* `basename $i`" >>$BASEDIR/doc/packages-list
	fi
  done
  echo "== List of softwares used to build $NAME Version: $VERSION ==" > $BASEDIR/doc/packages-list.txt
  grep -v 'configroot$\|img$\|initrd$\|initscripts$\|installer$\|install$\|setup$\|pakfire$\|stage2$\|smp$\|tools$\|tools1$\|tools2$\|.tgz$\|-config$\|_missing_rootfile$\|install1$\|install2$\|pass1$\|pass2$\|pass3$' \
	$BASEDIR/doc/packages-list | sort >> $BASEDIR/doc/packages-list.txt
  rm -f $BASEDIR/doc/packages-list
  # packages-list.txt is ready to be displayed for wiki page
  print_status DONE
  
  # Update changelog
  cd $BASEDIR
  [ -z $GIT_TAG ]  || LAST_TAG=$GIT_TAG
  [ -z $LAST_TAG ] || EXT="$LAST_TAG..HEAD"
  git log -n 500 --no-merges --pretty=medium --shortstat $EXT > $BASEDIR/doc/ChangeLog

  # Create images for install
  lfsmake2 cdrom

  # Check if there is a loop device for building in virtual environments
  modprobe loop 2>/dev/null
  if [ $BUILD_IMAGES == 1 ] && ([ -e /dev/loop/0 ] || [ -e /dev/loop0 ] || [ -e "/dev/loop-control" ]); then
	lfsmake2 flash-images
  fi

  mv $LFS/install/images/{*.iso,*.img.xz,*.bz2} $BASEDIR >> $LOGFILE 2>&1

  ipfirepackages

  cd $BASEDIR

  # remove not useable iso on armv5tel (needed to build flash images)
  [ "${BUILD_ARCH}" = "armv5tel" ] && rm -rf *.iso

  for i in $(ls *.bz2 *.img.xz *.iso 2>/dev/null); do
	md5sum $i > $i.md5
  done
  cd $PWD

  # Cleanup
  stdumount
  rm -rf $BASEDIR/build/tmp/*

  cd $PWD
}

ipfirepackages() {
	lfsmake2 core-updates

	local i
	for i in $(find $BASEDIR/config/rootfiles/packages{/${BUILD_ARCH},} -maxdepth 1 -type f); do
		i=$(basename ${i})
		if [ -e $BASEDIR/lfs/$i ]; then
			ipfiredist $i
		else
			echo -n $i
			print_status SKIP
		fi
	done
  test -d $BASEDIR/packages || mkdir $BASEDIR/packages
  mv -f $LFS/install/packages/* $BASEDIR/packages >> $LOGFILE 2>&1
  rm -rf  $BASEDIR/build/install/packages/*
}

while [ $# -gt 0 ]; do
	case "${1}" in
		--target=*)
			configure_build "${1#--target=}"
			;;
		-*)
			exiterror "Unknown configuration option: ${1}"
			;;
		*)
			# Found a command, so exit options parsing.
			break
			;;
	esac
	shift
done

# See what we're supposed to do
case "$1" in 
build)
	START_TIME=$(now)

	# Clear screen
	${INTERACTIVE} && clear

	PACKAGE=`ls -v -r $BASEDIR/cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}.tar.xz 2> /dev/null | head -n 1`
	#only restore on a clean disk
	if [ ! -e "${BASEDIR}/build${TOOLS_DIR}/.toolchain-successful" ]; then
		if [ ! -n "$PACKAGE" ]; then
			print_build_stage "Full toolchain compilation"
			prepareenv
			buildtoolchain
		else
			PACKAGENAME=${PACKAGE%.tar.xz}
			print_build_stage "Packaged toolchain compilation"
			if [ `md5sum $PACKAGE | awk '{print $1}'` == `cat $PACKAGENAME.md5 | awk '{print $1}'` ]; then
				tar axf $PACKAGE
				prepareenv
			else
				exiterror "$PACKAGENAME md5 did not match, check downloaded package"
			fi
		fi
	else
		prepareenv
	fi

	print_build_stage "Building LFS"
	buildbase

	print_build_stage "Building IPFire"
	buildipfire

	print_build_stage "Building installer"
	buildinstaller

	print_build_stage "Building packages"
	buildpackages
	
	print_build_stage "Checking Logfiles for new Files"

	cd $BASEDIR
	tools/checknewlog.pl
	tools/checkrootfiles
	cd $PWD

	print_build_summary $(( $(now) - ${START_TIME} ))
	;;
shell)
	# enter a shell inside LFS chroot
	# may be used to changed kernel settings
	prepareenv
	entershell
	;;
clean)
	print_line "Cleaning build directory..."

	for i in `mount | grep $BASEDIR | sed 's/^.*loop=\(.*\))/\1/'`; do
		$LOSETUP -d $i 2>/dev/null
	done
	#for i in `mount | grep $BASEDIR | cut -d " " -f 1`; do
	#	umount $i
	#done
	stdumount
	for i in `seq 0 7`; do
		if ( losetup /dev/loop${i} 2>/dev/null | grep -q "/install/images" ); then
		umount /dev/loop${i}     2>/dev/null;
		losetup -d /dev/loop${i} 2>/dev/null;
		fi;
	done
	rm -rf $BASEDIR/build
	rm -rf $BASEDIR/cdrom
	rm -rf $BASEDIR/packages
	rm -rf $BASEDIR/log
	if [ -h "${TOOLS_DIR}" ]; then
		rm -f "${TOOLS_DIR}"
	fi
	rm -f $BASEDIR/ipfire-*
	print_status DONE
	;;
docker)
	# Build the docker image if it does not exist, yet
	if ! docker images -a | grep -q ^ipfire-builder; then
		if docker build -t ipfire-builder ${BASEDIR}/tools/docker; then
			print_status DONE
		else
			print_status FAIL
			exit 1
		fi
	fi

	# Run the container and enter a shell
	docker run -it --privileged -v "${BASEDIR}:/build" -w "/build" ipfire-builder bash -l
	;;
downloadsrc)
	if [ ! -d $BASEDIR/cache ]; then
		mkdir $BASEDIR/cache
	fi
	mkdir -p $BASEDIR/log
	echo -e "${BOLD}Preload all source files${NORMAL}" | tee -a $LOGFILE
	FINISHED=0
	cd $BASEDIR/lfs
	for c in `seq $MAX_RETRIES`; do
		if (( FINISHED==1 )); then 
			break
		fi
		FINISHED=1
		cd $BASEDIR/lfs
		for i in *; do
			if [ -f "$i" -a "$i" != "Config" ]; then
				lfsmakecommoncheck ${i} || continue

				make -s -f $i LFS_BASEDIR=$BASEDIR BUILD_ARCH="${BUILD_ARCH}" \
					MESSAGE="$i\t ($c/$MAX_RETRIES)" download >> $LOGFILE 2>&1
				if [ $? -ne 0 ]; then
					print_status FAIL
					FINISHED=0
				else
					if [ $c -eq 1 ]; then
					print_status DONE
					fi
				fi
			fi
		done
	done
	echo -e "${BOLD}***Verifying md5sums${NORMAL}"
	ERROR=0
	for i in *; do
		if [ -f "$i" -a "$i" != "Config" ]; then
			lfsmakecommoncheck ${i} > /dev/null || continue
			make -s -f $i LFS_BASEDIR=$BASEDIR BUILD_ARCH="${BUILD_ARCH}" \
				MESSAGE="$i\t " md5 >> $LOGFILE 2>&1
			if [ $? -ne 0 ]; then
				echo -ne "MD5 difference in lfs/$i"
				print_status FAIL
				ERROR=1
			fi
		fi
	done
	if [ $ERROR -eq 0 ]; then
		echo -ne "${BOLD}all files md5sum match${NORMAL}"
		print_status DONE
	else
		echo -ne "${BOLD}not all files were correctly download${NORMAL}"
		print_status FAIL
	fi
	cd - >/dev/null 2>&1
	;;
toolchain)
	# Clear screen
	${INTERACTIVE} && clear

	prepareenv
	print_build_stage "Toolchain compilation (${BUILD_ARCH})"
	buildtoolchain
	echo "`date -u '+%b %e %T'`: Create toolchain image for ${BUILD_ARCH}" | tee -a $LOGFILE
	test -d $BASEDIR/cache/toolchains || mkdir -p $BASEDIR/cache/toolchains
	cd $BASEDIR && tar -cf- --exclude='log/_build.*.log' build/${TOOLS_DIR} build/bin/sh log | xz ${XZ_OPT} \
		> cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}.tar.xz
	md5sum cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}.tar.xz \
		> cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}.md5
	stdumount
	;;
gettoolchain)
	# arbitrary name to be updated in case of new toolchain package upload
	PACKAGE=$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}
	if [ ! -f $BASEDIR/cache/toolchains/$PACKAGE.tar.xz ]; then
		URL_TOOLCHAIN=`grep URL_TOOLCHAIN lfs/Config | awk '{ print $3 }'`
		test -d $BASEDIR/cache/toolchains || mkdir -p $BASEDIR/cache/toolchains
		echo "`date -u '+%b %e %T'`: Load toolchain image for ${BUILD_ARCH}" | tee -a $LOGFILE
		cd $BASEDIR/cache/toolchains
		wget -U "IPFireSourceGrabber/2.x" $URL_TOOLCHAIN/$PACKAGE.tar.xz $URL_TOOLCHAIN/$PACKAGE.md5 >& /dev/null
		if [ $? -ne 0 ]; then
			echo "`date -u '+%b %e %T'`: error downloading $PACKAGE toolchain for ${BUILD_ARCH} machine" | tee -a $LOGFILE
		else
			if [ "`md5sum $PACKAGE.tar.xz | awk '{print $1}'`" = "`cat $PACKAGE.md5 | awk '{print $1}'`" ]; then
				echo "`date -u '+%b %e %T'`: toolchain md5 ok" | tee -a $LOGFILE
			else
				exiterror "$PACKAGE.md5 did not match, check downloaded package"
			fi
		fi
	else
		echo "Toolchain is already downloaded. Exiting..."
	fi
	;;
uploadsrc)
	PWD=`pwd`
	if [ -z $IPFIRE_USER ]; then
		echo -n "You have to setup IPFIRE_USER first. See .config for details."
		print_status FAIL
		exit 1
	fi

	URL_SOURCE=$(grep URL_SOURCE lfs/Config | awk '{ print $3 }')
	REMOTE_FILES=$(echo "ls -1" | sftp -C ${IPFIRE_USER}@${URL_SOURCE})

	for file in ${BASEDIR}/cache/*; do
		[ -d "${file}" ] && continue
		grep -q "$(basename ${file})" <<<$REMOTE_FILES && continue
		NEW_FILES="$NEW_FILES $file"
	done
	[ -n "$NEW_FILES" ] && scp -2 $NEW_FILES ${IPFIRE_USER}@${URL_SOURCE}
	cd $BASEDIR
	cd $PWD
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
	$BASEDIR/tools/check_strings.pl en > $BASEDIR/doc/language_issues.en
	$BASEDIR/tools/check_strings.pl de > $BASEDIR/doc/language_issues.de
	$BASEDIR/tools/check_strings.pl fr > $BASEDIR/doc/language_issues.fr
	$BASEDIR/tools/check_strings.pl es > $BASEDIR/doc/language_issues.es
	$BASEDIR/tools/check_strings.pl es > $BASEDIR/doc/language_issues.pl
	$BASEDIR/tools/check_strings.pl ru > $BASEDIR/doc/language_issues.ru
	$BASEDIR/tools/check_strings.pl nl > $BASEDIR/doc/language_issues.nl
	$BASEDIR/tools/check_strings.pl tr > $BASEDIR/doc/language_issues.tr
	$BASEDIR/tools/check_strings.pl it > $BASEDIR/doc/language_issues.it
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
	exec "${BASEDIR}/tools/find-dependencies" "${BASEDIR}/build" "$@"
	;;
*)
	echo "Usage: $0 {build|changelog|clean|gettoolchain|downloadsrc|shell|sync|toolchain|update-contributors|find-dependencies}"
	cat doc/make.sh-usage
	;;
esac

