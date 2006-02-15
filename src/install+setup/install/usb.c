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
 * $Id: usb.c,v 1.9.2.8 2005/12/10 00:18:23 franck78 Exp $
 * 
 */

#include "install.h"

int usbuhci = 0;
int usbohci = 0;
int ehcihcd = 0;

int initialize_usb() {
    modprobe("sd_mod");
    modprobe("sr_mod");
    modprobe("usb-storage");

    if (ehcihcd) {
    	rmmod("ehci-hcd");
    	ehcihcd = 0;
    }
    if (usbohci) {
    	rmmod("usb-ohci");
    	usbohci = 0;
    }
    if (usbuhci) {
    	rmmod("usb-uhci");
    	usbuhci = 0;
    }

    if (modprobe("ehci-hcd") == 0) ehcihcd = 1;
    if (modprobe("usb-ohci") == 0) usbohci = 1;
    if (modprobe("usb-uhci") == 0) usbuhci = 1;

    modprobe("hid");
    modprobe("keybdev");
    return 0;
}

int write_usb_modules_conf() {
    int index = 0;
    FILE *handle;

    if (!(handle = fopen("/harddisk/etc/modules.conf", "a")))
    	return 0;

#if 0 /* we don't do this yet, because one of the drivers has a problem 
       * with it */
    if (ehcihcd) {
	fprintf(handle,"alias usb-controller");
	if (index)
		fprintf(handle,"%d",index);
	fprintf(handle," ehci-hcd\n");
	index++;
    }
#endif

    if (usbohci) {
	fprintf(handle,"alias usb-controller");
	if (index)
		fprintf(handle,"%d",index);
	fprintf(handle," usb-ohci\n");
	index++;
    }

    if (usbuhci) {
	fprintf(handle,"alias usb-controller");
	if (index)
		fprintf(handle,"%d",index);
	fprintf(handle," usb-uhci\n");
	index++;
    }
    fclose(handle);
    
    return 0;
}

/* checkusb().
    Scans the named partitions and returns true if USB-removable.
    a bug? in "cat /proc/partitions" with superfloppy scheme device
    make them appearing always with four 'false' partitions:
    sda and sda1 sda2 sda3 sda4.
    No easy way to decide if /dev/sda1 exists or not.
*/
int checkusb(char *partition)
{
	FILE *f = NULL;
	char filename[STRING_SIZE];
	char buffer[STRING_SIZE];
	char *pchar = &buffer[0];
	if (!(f = fopen("/proc/partitions", "r")))
		return 0;

	short int major = 0, minor = 0;			
	while (fgets(buffer, STRING_SIZE, f))	{
	    /* look for partition*/	
	    if (strstr (buffer, partition)) {
		major = atoi (buffer);
		if (major != 8) break ; /* not scsi */
		//get minor
		while (*pchar != '8') pchar++;
		minor = atoi (++pchar);
		break;
	    }
	}
	fclose(f);
	if (major != 8) return 0; /* nothing found */
	
	//now check for usb-storage-MINOR
	minor >>= 4; // get index from minor
	sprintf (filename, "/proc/scsi/usb-storage-%d/%d", minor,minor);

	if (!(f = fopen(filename, "r")))
		return 0;
	int count = 0;
	while (fgets(buffer, STRING_SIZE, f))	{
	    if (strstr(buffer,"usb-storage")) count++;
	    if (strstr(buffer,"SCSI")) count++;
	    if (strstr(buffer,"Attached: Yes")) count++;
	}
	fclose(f);
	
	return (count==3 ? 1 : 0);
}
