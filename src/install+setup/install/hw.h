/*#############################################################################
#                                                                             #
# IPFire - An Open Source Firewall Distribution                               #
# Copyright (C) 2014 IPFire development team                                  #
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
#############################################################################*/

#ifndef HEADER_HW_H
#define HEADER_HW_H

#include <libudev.h>

#define SOURCE_MOUNT_PATH "/cdrom"
#define SOURCE_TEST_FILE  SOURCE_MOUNT_PATH "/" VERSION ".media"

struct hw {
	struct udev *udev;
};

struct hw* hw_init();
void hw_free(struct hw* hw);

int hw_mount(const char* source, const char* target, int flags);
int hw_umount(const char* target);

char* hw_find_source_medium(struct hw* hw);

#endif /* HEADER_HW_H */
