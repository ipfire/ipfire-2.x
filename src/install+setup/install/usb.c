/*
 * This file is part of the IPCop Firewall.
 *
 * IPCop is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * IPCop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 * Copyright 2002: Mark Wormgoor <mark@wormgoor.com>
 * 
 */

#include "install.h"

int usbuhci = 0;
int usbohci = 0;
int ehcihcd = 0;

int initialize_usb() {
    mysystem("/sbin/modprobe sd_mod");
    mysystem("/sbin/modprobe sr_mod");
    mysystem("/sbin/modprobe usb-storage");

    if (ehcihcd) {
    	mysystem("/sbin/rmmod ehci-hcd");
    	ehcihcd = 0;
    }
    if (usbohci) {
    	mysystem("/sbin/rmmod ohci-hcd");
    	usbohci = 0;
    }
    if (usbuhci) {
    	mysystem("/sbin/rmmod uhci-hcd");
    	usbuhci = 0;
    }

    if (mysystem("/sbin/modprobe ehci-hcd") == 0)
    	ehcihcd = 1;
    if (mysystem("/sbin/modprobe ohci-hcd") == 0)
    	usbohci = 1;
    if (mysystem("/sbin/modprobe uhci-hcd") == 0)
    	usbuhci = 1;

    mysystem("/sbin/modprobe usbhid");
    mysystem("udevstart");
    return 0;
}

int write_usb_modules_conf() {
    int index;
    FILE *handle;

    if (!(handle = fopen("/harddisk/etc/modules.conf", "a")))
    	return 0;

    index = 0;

#if 0 /* we don't do this yet, because one of the drivers has a problem 
       * with it */
    if (ehcihcd) {
	if (index)
		fprintf(handle,"alias usb-controller%d ehci-hcd\n",index);
	else
		fprintf(handle,"alias usb-controller ehci-hcd\n");
	index++;
    }
#endif

    if (usbohci) {
	if (index)
		fprintf(handle,"alias usb-controller%d ohci-hcd\n",index);
	else
		fprintf(handle,"alias usb-controller ohci-hcd\n");
	index++;
    }

    if (usbuhci) {
	if (index)
		fprintf(handle,"alias usb-controller%d uhci-hcd\n",index);
	else
		fprintf(handle,"alias usb-controller uhci-hcd\n");
	index++;
    }
    fclose(handle);
    
    return 0;
}
