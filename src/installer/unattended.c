/*
 * This file is part of the IPFire Firewall.
 *
 * IPFire is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * IPFire is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with IPFire; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 * Copyright 2007: Michael Tremer for www.ipfire.org
 * 
 */

#include "install.h"
extern FILE *flog;

int unattended_setup(struct keyvalue *unattendedkv) {

    struct keyvalue *mainsettings = initkeyvalues();
    struct keyvalue *ethernetkv = initkeyvalues();
    FILE *file, *hosts;
    char commandstring[STRING_SIZE];

    char domainname[STRING_SIZE];
    char hostname[STRING_SIZE];
    char keymap[STRING_SIZE];
    char language[STRING_SIZE];
    char timezone[STRING_SIZE];
    char theme[STRING_SIZE];
    char green_address[STRING_SIZE];
    char green_netmask[STRING_SIZE];
    char green_netaddress[STRING_SIZE];
    char green_broadcast[STRING_SIZE];
    char root_password[STRING_SIZE];
    char admin_password[STRING_SIZE];
    char restore_file[STRING_SIZE] = "";

    findkey(unattendedkv, "DOMAINNAME", domainname);
    findkey(unattendedkv, "HOSTNAME", hostname);
    findkey(unattendedkv, "KEYMAP", keymap);
    findkey(unattendedkv, "LANGUAGE", language);
    findkey(unattendedkv, "TIMEZONE", timezone);
    findkey(unattendedkv, "THEME", theme);
    findkey(unattendedkv, "GREEN_ADDRESS", green_address);
    findkey(unattendedkv, "GREEN_NETMASK", green_netmask);
    findkey(unattendedkv, "GREEN_NETADDRESS", green_netaddress);
    findkey(unattendedkv, "GREEN_BROADCAST", green_broadcast);
    findkey(unattendedkv, "ROOT_PASSWORD", root_password);
    findkey(unattendedkv, "ADMIN_PASSWORD", admin_password);
    findkey(unattendedkv, "RESTORE_FILE", restore_file);

    /* write main/settings. */
    replacekeyvalue(mainsettings, "DOMAINNAME", domainname);
    replacekeyvalue(mainsettings, "HOSTNAME", hostname);
    replacekeyvalue(mainsettings, "KEYMAP", keymap);
    replacekeyvalue(mainsettings, "LANGUAGE", language);
    replacekeyvalue(mainsettings, "TIMEZONE", timezone);
    replacekeyvalue(mainsettings, "THEME", theme);
    writekeyvalues(mainsettings, "/harddisk" CONFIG_ROOT "/main/settings");
    freekeyvalues(mainsettings);

    /* do setup stuff */
    fprintf(flog, "unattended: Starting setup\n");

    /* network */
    fprintf(flog, "unattended: setting up network configuration\n");

    (void) readkeyvalues(ethernetkv, "/harddisk" CONFIG_ROOT "/ethernet/settings");
    replacekeyvalue(ethernetkv, "GREEN_ADDRESS", green_address);
    replacekeyvalue(ethernetkv, "GREEN_NETMASK", green_netmask);
    replacekeyvalue(ethernetkv, "GREEN_NETADDRESS", green_netaddress);
    replacekeyvalue(ethernetkv, "GREEN_BROADCAST", green_broadcast);
    replacekeyvalue(ethernetkv, "CONFIG_TYPE", "0");
    replacekeyvalue(ethernetkv, "GREEN_DEV", "eth0");
    writekeyvalues(ethernetkv, "/harddisk" CONFIG_ROOT "/ethernet/settings");
    freekeyvalues(ethernetkv);

    /* timezone */
    unlink("/harddisk/etc/localtime");
    snprintf(commandstring, STRING_SIZE, "/harddisk/%s", timezone);
    link(commandstring, "/harddisk/etc/localtime");

    /* hostname */
    fprintf(flog, "unattended: writing hostname.conf\n");
    if (!(file = fopen("/harddisk" CONFIG_ROOT "/main/hostname.conf", "w")))
    {
	errorbox("unattended: ERROR writing hostname.conf");
	return 0;
    }
    fprintf(file, "ServerName %s.%s\n", hostname,domainname);
    fclose(file);

    fprintf(flog, "unattended: writing hosts\n");
    if (!(hosts = fopen("/harddisk/etc/hosts", "w")))
    {
	errorbox("unattended: ERROR writing hosts");
	return 0;
    }
    fprintf(hosts, "127.0.0.1\tlocalhost\n");
    fprintf(hosts, "%s\t%s.%s\t%s\n", green_address, hostname, domainname, hostname);
    fclose(hosts);

    fprintf(flog, "unattended: writing hosts.allow\n");
    if (!(file = fopen("/harddisk/etc/hosts.allow", "w")))
    {
	errorbox("unattended: ERROR writing hosts.allow");
	return 0;
    }
    fprintf(file, "sshd : ALL\n");
    fprintf(file, "ALL  : localhost\n");
    fprintf(file, "ALL  : %s/%s\n", green_netaddress, green_netmask);
    fclose(file);

    fprintf(flog, "unattended: writing hosts.deny\n");
    if (!(file = fopen("/harddisk/etc/hosts.deny", "w")))
    {
	errorbox("unattended: ERROR writing hosts.deny");
        return 0;
    }
    fprintf(file, "ALL : ALL\n");
    fclose(file);

    /* set root password */
    fprintf(flog, "unattended: setting root password\n");
    snprintf(commandstring, STRING_SIZE,
	    "/usr/sbin/chroot /harddisk /bin/sh -c \"echo 'root:%s' | /usr/sbin/chpasswd\"", root_password);
    if (mysystem(commandstring)) {
	errorbox("unattended: ERROR setting root password");
	return 0;
    }

    /* set admin password */
    fprintf(flog, "unattended: setting admin password\n");
    snprintf(commandstring, STRING_SIZE,
	    "/usr/sbin/chroot /harddisk /usr/sbin/htpasswd -c -m -b " CONFIG_ROOT "/auth/users admin '%s'", admin_password);
    if (mysystem(commandstring)) {
	errorbox("unattended: ERROR setting admin password");
	return 0;
    }

	/* restore backup */
	if (strlen(restore_file) > 0) {
		fprintf(flog, "unattended: Restoring Backup\n");
	    snprintf(commandstring, STRING_SIZE,
		    "/usr/sbin/chroot /harddisk /bin/tar -xvzp -f /var/ipfire/backup/%s -C /", restore_file);
	    if (mysystem(commandstring)) {
	    	errorbox("unattended: ERROR restoring backup");
	    }
	}

    fprintf(flog, "unattended: Setup ended\n");
    return 1;
}
