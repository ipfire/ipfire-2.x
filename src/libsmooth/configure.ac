#  This file is part of libsmooth.
#
#  libsmooth is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.

AC_PREREQ([2.64])

AC_INIT([libsmooth],
	[001],
	[],
	[libsmooth],
	[http://git.ipfire.org/?p=ipfire-2.x.git;a=summary])

AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_AUX_DIR([build-aux])

AM_INIT_AUTOMAKE([
	foreign
	1.11
	-Wall
	-Wno-portability
	silent-rules
	tar-pax
	no-dist-gzip
	dist-xz
	subdir-objects
])
AM_SILENT_RULES([yes])

LT_PREREQ(2.2)
LT_INIT([disable-static])

AC_PROG_SED

AC_PROG_CC
AC_PROG_CC_C99
AC_PROG_CC_C_O

AC_PATH_PROG([M4], [m4])

# This makes sure pkg.m4 is available.
m4_pattern_forbid([^_?PKG_[A-Z_]+$],[*** pkg.m4 missing, please install pkg-config])

AC_CONFIG_FILES([
	Makefile
])

AC_OUTPUT
AC_MSG_RESULT([
	$PACKAGE_NAME $VERSION

	CFLAGS:			${OUR_CFLAGS} ${CFLAGS}
	CPPFLAGS:		${OUR_CPPFLAGS} ${CPPFLAGS}
	LDFLAGS:		${OUR_LDFLAGS} ${LDFLAGS}
])
