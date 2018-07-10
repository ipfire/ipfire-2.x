#  This file is part of the setup tool.
#
#  setup is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.

ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}
AM_MAKEFLAGS = --no-print-directory
AUTOMAKE_OPTIONS = color-tests parallel-tests

SUBDIRS = . po

# remove targets if the command fails
.DELETE_ON_ERROR:

# keep intermediate files
.SECONDARY:

AM_CPPFLAGS = \
	-include $(top_builddir)/config.h \
	$(OUR_CPPFLAGS)

AM_CFLAGS = $(OUR_CFLAGS)
AM_CXXFLAGS = $(OUR_CXXFLAGS)
AM_LDFLAGS = $(OUR_LDFLAGS)

sudodir = /etc/sudoers.d

bin_SCRIPTS =
sbin_PROGRAMS =

#- setup -----------------------------------------------------------------------

bin_SCRIPTS += \
	run-setup

sbin_PROGRAMS += \
	setup

setup_SOURCES = \
	dhcp.c \
	domainname.c \
	hostname.c \
	keymap.c \
	main.c \
	misc.c \
	netstuff.c \
	networking.c \
	passwords.c \
	setup.h \
	timezone.c

setup_CFLAGS = \
	$(AM_CFLAGS) \
	$(LIBSMOOTH_CFLAGS)

setup_LDADD = \
	$(LIBSMOOTH_LIBS) \
	$(NEWT_LIBS)

bin_SCRIPTS += \
	probenic.sh

sudo_DATA = \
	sudo/setup
