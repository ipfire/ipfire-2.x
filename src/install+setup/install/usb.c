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
 * $Id: usb.c,v 1.9.2.3 2004/11/16 22:48:43 alanh Exp $
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
    	mysystem("/sbin/rmmod usb-ohci");
    	usbohci = 0;
    }
    if (usbuhci) {
    	mysystem("/sbin/rmmod usb-uhci");
    	usbuhci = 0;
    }

    if (mysystem("/sbin/modprobe ehci-hcd") == 0)
    	ehcihcd = 1;
    if (mysystem("/sbin/modprobe usb-ohci") == 0)
    	usbohci = 1;
    if (mysystem("/sbin/modprobe usb-uhci") == 0)
    	usbuhci = 1;

    mysystem("/sbin/modprobe hid");
    mysystem("/sbin/modprobe keybdev");
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
		fprintf(handle,"alias usb-controller%d usb-ohci\n",index);
	else
		fprintf(handle,"alias usb-controller usb-ohci\n");
	index++;
    }

    if (usbuhci) {
	if (index)
		fprintf(handle,"alias usb-controller%d usb-uhci\n",index);
	else
		fprintf(handle,"alias usb-controller usb-uhci\n");
	index++;
    }
    fclose(handle);
    
    return 0;
}
