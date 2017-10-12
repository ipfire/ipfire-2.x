#  This file is part of the installer.
#
#  installer is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.

AC_PREREQ([2.64])

AC_INIT([installer],
	[001],
	[],
	[installer],
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

CC_CHECK_FLAGS_APPEND([with_cflags], [CFLAGS], [\
	"-Wformat=2 -Wformat-security -Wformat-nonliteral" \
	-Werror=overflow \
	-fno-strict-aliasing \
	-fstack-protector \
	-fstack-protector-strong \
	-fPIE \
	--param=ssp-buffer-size=4])
AC_SUBST([OUR_CFLAGS], "$with_cflags")

AC_PATH_PROG([M4], [m4])

# Gettext
AM_GNU_GETTEXT([external])
AM_GNU_GETTEXT_VERSION([0.18])
AC_CHECK_HEADERS([libintl.h])

# This makes sure pkg.m4 is available.
m4_pattern_forbid([^_?PKG_[A-Z_]+$],[*** pkg.m4 missing, please install pkg-config])

save_LIBS="$LIBS"

# newt
LIBS=
AC_SEARCH_LIBS([newtWinMenu], [newt], [], [AC_MSG_ERROR([*** newt library not found])])
NEWT_LIBS="$LIBS"
AC_SUBST(NEWT_LIBS)

LIBS="$save_LIBS"

PKG_CHECK_MODULES(BLKID, [blkid])
PKG_CHECK_MODULES(PCI, [libpci])
PKG_CHECK_MODULES(LIBSMOOTH, [libsmooth])
PKG_CHECK_MODULES(UDEV, [libudev])

AC_ARG_WITH([distro-name],
	AS_HELP_STRING([--with-distro-name] [The name of the distribution]),
	AC_DEFINE_UNQUOTED([DISTRO_NAME], "$withval", [The name of the distribution]),
	AC_MSG_ERROR([*** you need to set the name with --with-distro-name=]))

AC_ARG_WITH([distro-sname],
	AS_HELP_STRING([--with-distro-sname] [The short name of the distribution]),
	AC_DEFINE_UNQUOTED([DISTRO_SNAME], "$withval", [The sname of the distribution]),
	AC_MSG_ERROR([*** you need to set the sname with --with-distro-sname=]))

AC_ARG_WITH([distro-version],
	AS_HELP_STRING([--with-distro-sname] [The version of the distribution]),
	AC_DEFINE_UNQUOTED([DISTRO_VERSION], "$withval", [The version of the distribution]),
	AC_MSG_ERROR([*** you need to set the version with --with-distro-version=]))

AC_ARG_WITH([distro-slogan],
	AS_HELP_STRING([--with-distro-slogan] [The slogan of the distribution]),
	AC_DEFINE_UNQUOTED([DISTRO_SLOGAN], "$withval", [The slogan of the distribution]),
	AC_MSG_ERROR([*** you need to set the slogan with --with-distro-slogan=]))

AC_ARG_WITH([config-root],
	AS_HELP_STRING([--with-distro-config-root] [The configuration directory]),
	AC_DEFINE_UNQUOTED([CONFIG_ROOT], "$withval", [The config-root]),
	AC_MSG_ERROR([*** you need to set CONFIG_ROOT with --with-config-root=]))

AC_ARG_WITH([download-url],
	AS_HELP_STRING([--with-download-url] [The default download URL]),
	AC_DEFINE_UNQUOTED([DOWNLOAD_URL], "$withval", [The default download URL]),
	AC_MSG_ERROR([*** you need to set DOWNLOAD_URL with --with-download-url=]))

AC_CONFIG_FILES([
	Makefile
	po/Makefile.in
])

AC_OUTPUT
AC_MSG_RESULT([
	$PACKAGE_NAME $VERSION

	CFLAGS:			${OUR_CFLAGS} ${CFLAGS}
	CPPFLAGS:		${OUR_CPPFLAGS} ${CPPFLAGS}
	LDFLAGS:		${OUR_LDFLAGS} ${LDFLAGS}

	Distribution:		${DISTRO_NAME} (${DISTRO_SNAME})
	Version:		${DISTRO_VERSION}
	Slogan:			${DISTRO_SLOGAN}
	Config Root:		${CONFIG_ROOT}
])
