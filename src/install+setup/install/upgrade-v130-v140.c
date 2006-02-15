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
 * $Id: upgrade-v130-v140.c,v 1.12.2.35 2004/11/11 09:40:03 alanh Exp $
 * 
 */

#include "install.h"

extern char **ctr;
 
int _handledomainname(void)
{
	char domainname[STRING_SIZE] = "localdomain";
	struct keyvalue *kv = initkeyvalues();
	char *values[] = { domainname, NULL };	/* pointers for the values. */
	struct newtWinEntry entries[] =
		{ { "", &values[0], 0,}, { NULL, NULL, 0 } };
	int rc;
	int result;
	
	if (!(readkeyvalues(kv, "/harddisk" CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}	
	
	findkey(kv, "DOMAINNAME", domainname);

	/* already have a domainname */
	if (strlen(domainname))
		return 0;
	
	for (;;)
	{	
		rc = newtWinEntries(ctr[TR_DOMAINNAME], ctr[TR_ENTER_DOMAINNAME],
			50, 5, 5, 40, entries, ctr[TR_OK], ctr[TR_CANCEL], NULL);	
		
		if (rc == 1)
		{
			strcpy(domainname, values[0]);
			if (strchr(domainname, ' '))
				errorbox(ctr[TR_DOMAINNAME_CANNOT_CONTAIN_SPACES]);
			else
			{			
				replacekeyvalue(kv, "DOMAINNAME", domainname);
				writekeyvalues(kv, "/harddisk" CONFIG_ROOT "/main/settings");
				result = 1;
				break;
			}
		}
		else
		{
			result = 0;
			break;
		}
	}
	free(values[0]);
	freekeyvalues(kv);
	
	return result;
}	

int _add_logwatch_user() {
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel logwatch");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel logwatch");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupadd -g 102 logwatch");
	mysystem("/bin/chroot /harddisk /usr/sbin/useradd  -u 102 -g logwatch -d /var/log/logwatch -s /bin/false logwatch");
    
	return 0;
}

int _fixsquid() {
	FILE *squidreadfile;
	FILE *squidwritefile;
	FILE *aclreadfile;
	char hostname[STRING_SIZE] = "";
	char domainname[STRING_SIZE] = "";
	char squidtemp[STRING_SIZE];
	struct keyvalue *kv = initkeyvalues();
	int already_upgraded = 0;
	int updated = 0;

	if (!(squidreadfile = fopen ("/harddisk" CONFIG_ROOT "/proxy/squid.conf", "r"))) return 1;
	if (!(squidwritefile = fopen ("/harddisk" CONFIG_ROOT "/proxy/squid.conf.new", "w"))) 
	{
		fclose(squidreadfile);
		return 1;
	}

	if (!(readkeyvalues(kv, "/harddisk" CONFIG_ROOT "/main/settings")))
	{
		fclose (squidwritefile);
		fclose (squidreadfile);
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 1;
	}

	findkey(kv, "HOSTNAME", hostname);
	findkey(kv, "DOMAINNAME", domainname);
	freekeyvalues(kv);

        while (fgets (squidtemp, STRING_SIZE, squidreadfile) != NULL) {
		/* this will fail if we've already been upgraded, which is ok */
		if (!strncmp(squidtemp, "reply_body_max_size 0 KB", 24)) {
			sprintf(squidtemp, "reply_body_max_size 0 allow all\n");
		}
		if (!strncmp(squidtemp, "cache_store_log /var/log/squid/store.log", 40)) {
			sprintf(squidtemp, "cache_store_log none\n");
		}
		fputs(squidtemp, squidwritefile);

		/* so for us developers we skip already upgraded squiddies */
		if (!strncmp(squidtemp, "visible_hostname", 16)) {
			already_upgraded = 1;
		}

		/* Check for the new acl's */
		if (!strncmp(squidtemp, "__GREEN_IP__", 12)) {
			updated = 1;
		}
	}
	if (!already_upgraded) {
		sprintf(squidtemp, "visible_hostname %s.%s\n", hostname, domainname);
		fputs(squidtemp, squidwritefile);
	}

	fclose (squidwritefile);
	fclose (squidreadfile);

	rename ("/harddisk" CONFIG_ROOT "/proxy/squid.conf.new",
		"/harddisk" CONFIG_ROOT "/proxy/squid.conf");

	replace("/harddisk" CONFIG_ROOT "/proxy/squid.conf", "cache_dir ufs", "cache_dir aufs");

	if (!updated) {
		rename ("/harddisk" CONFIG_ROOT "/proxy/acl",
			"/harddisk" CONFIG_ROOT "/proxy/acl.old");
		rename ("/harddisk" CONFIG_ROOT "/proxy/acl-1.4",
			"/harddisk" CONFIG_ROOT "/proxy/acl");
	} else {
		if (!(aclreadfile = fopen ("/harddisk" CONFIG_ROOT "/proxy/acl", "r"))) {
			rename ("/harddisk" CONFIG_ROOT "/proxy/acl-1.4",
				"/harddisk" CONFIG_ROOT "/proxy/acl");
		} else {
			unlink ("/harddisk" CONFIG_ROOT "/proxy/acl-1.4");
			fclose(aclreadfile);
		}
	}

	chown  ("/harddisk" CONFIG_ROOT "/proxy/squid.conf", 99, 99);
	chown  ("/harddisk" CONFIG_ROOT "/proxy/acl", 99, 99);
	return 0;
}

int _fixeagleusb() {
	FILE *eaglereadfile;
	FILE *eaglewritefile;
	char eagletemp[STRING_SIZE];
	int already_upgraded = 0;

	if (!(eaglereadfile  = fopen ("/harddisk" CONFIG_ROOT "/eagle-usb/eagle-usb.conf", "r"))) return 1;
	if (!(eaglewritefile = fopen ("/harddisk" CONFIG_ROOT "/eagle-usb/eagle-usb.conf.new", "w"))) 
	{
		fclose(eaglereadfile);
		return 1;
	}

        while (fgets (eagletemp, STRING_SIZE, eaglereadfile) != NULL) {
		/* so for us developers we skip already upgraded configs */
		if (!strncmp(eagletemp, "<eaglectrl>", 11)) {
			already_upgraded = 1;
		}
	}

	rewind(eaglereadfile);
	if (!already_upgraded)
		fprintf(eaglewritefile, "<eaglectrl>\n");
	while (fgets (eagletemp, STRING_SIZE, eaglereadfile) != NULL)
		fputs(eagletemp, eaglewritefile);
	if (!already_upgraded)
		fprintf(eaglewritefile, "</eaglectrl>\n");

	fclose (eaglewritefile);
	fclose (eaglereadfile);

	rename ("/harddisk" CONFIG_ROOT "/eagle-usb/eagle-usb.conf.new",
		"/harddisk" CONFIG_ROOT "/eagle-usb/eagle-usb.conf");

	replace("/harddisk" CONFIG_ROOT "/eagle-usb/eagle-usb.conf", "Linetype=00000001", "Linetype=0A");

	chown  ("/harddisk" CONFIG_ROOT "/eagle-usb/eagle-usb.conf", 99, 99);
	unlink("/harddisk" CONFIG_ROOT "/eagle-usb/dsp_code_pots.bin");
	unlink("/harddisk" CONFIG_ROOT "/eagle-usb/dsp_code_isdn.bin");
	return 0;
}

int _fixdhcp_30() {
	FILE *dhcpreadfile;
	FILE *dhcpwritefile;
	char dhcptemp[STRING_SIZE];

	if (!(dhcpreadfile = fopen ("/harddisk" CONFIG_ROOT "/dhcp/dhcpd.conf", "r"))) return 1;
	if (!(dhcpwritefile = fopen ("/harddisk" CONFIG_ROOT "/dhcp/dhcpd.conf.new", "w"))) 
	{
		fclose(dhcpreadfile);
		return 1;
	}
	fprintf (dhcpwritefile, "authoritative;\n");
	fprintf (dhcpwritefile, "deny bootp;\n");
	fprintf (dhcpwritefile, "ddns-update-style none;\n");
	while (fgets (dhcptemp, STRING_SIZE, dhcpreadfile) != NULL) {
		int write = 1;

		/* so for us developers we skip already upgraded dhcp files */
		if (!strncmp(dhcptemp, "authoritative", 13)) {
			write = 0;
		}
		/* so for us developers we skip already upgraded dhcp files */
		if (!strncmp(dhcptemp, "ddns-update-style", 17)) {
			write = 0;
		}
		/* so for us developers we skip already upgraded dhcp files */
		if (!strncmp(dhcptemp, "deny bootp", 10)) {
			write = 0;
		}

		if (write)
			fputs(dhcptemp, dhcpwritefile);
	}

	fclose(dhcpreadfile);
	fclose(dhcpwritefile);

	rename ("/harddisk" CONFIG_ROOT "/dhcp/dhcpd.conf.new",
		"/harddisk" CONFIG_ROOT "/dhcp/dhcpd.conf");
	chown  ("/harddisk" CONFIG_ROOT "/dhcp/dhcpd.conf", 99, 99);

	/* This one will get converted again furthur down */
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "WINS=", "WINS1=");

	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "START_ADDR=", "START_ADDR_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "END_ADDR=", "END_ADDR_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "DOMAIN_NAME=", "DOMAIN_NAME_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "DEFAULT_LEASE_TIME=", "DEFAULT_LEASE_TIME_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "MAX_LEASE_TIME=", "MAX_LEASE_TIME_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "DNS1=", "DNS1_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "DNS2=", "DNS2_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "WINS1=", "WINS1_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "WINS2=", "WINS2_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "ENABLE=", "ENABLE_GREEN=");
	replace("/harddisk" CONFIG_ROOT "/dhcp/settings", "range dynamic-bootp", "range");
	chown  ("/harddisk" CONFIG_ROOT "/dhcp/settings", 99, 99);

	if ((dhcpreadfile = fopen ("/harddisk" CONFIG_ROOT "/dhcp/enable", "r")))
	{
		fclose(dhcpreadfile);
		rename ("/harddisk" CONFIG_ROOT "/dhcp/enable",
			"/harddisk" CONFIG_ROOT "/dhcp/enable_green");
		chown  ("/harddisk" CONFIG_ROOT "/dhcp/enable_green", 99, 99);
	}

	return 0;
}

int _add_sshd_user() {
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel sshd");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel sshd");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupadd -g 74 sshd");
	mysystem("/bin/chroot /harddisk /usr/sbin/useradd  -u 74 -g sshd -d /var/empty/sshd -s /bin/false -M sshd");
    
	return 0;
}

int _add_dnsmasq_user() {
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel dnsmasq");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel dnsmasq");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupadd -g 103 dnsmasq");
	mysystem("/bin/chroot /harddisk /usr/sbin/useradd  -u 103 -g dnsmasq -d / -s /bin/false -M dnsmasq");
    
	return 0;
}

int _add_cron_user() {
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel cron");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel cron");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupadd -g 104 cron");
	mysystem("/bin/chroot /harddisk /usr/sbin/useradd  -u 104 -g cron -d / -s /bin/false -M cron");
    
	return 0;
}

int _add_sysklogd_user() {
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel syslogd");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel syslogd");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupadd -g 105 syslogd");
	mysystem("/bin/chroot /harddisk /usr/sbin/useradd  -u 105 -g syslogd -d / -s /bin/false -M syslogd");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel klogd");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel klogd");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupadd -g 106 klogd");
	mysystem("/bin/chroot /harddisk /usr/sbin/useradd  -u 106 -g klogd -d / -s /bin/false -M klogd");
    
	return 0;
}

int _del_setup_user() {
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel setup");
    
	return 0;
}

int _create_nobody_dir(){
	mysystem("/bin/chroot /harddisk /usr/sbin/usermod -d /home/nobody nobody");

	return 0;
}

int _del_useless_user_group()
{
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel games");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel games");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel news");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel news");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel ftp");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel gopher");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel lp");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel uucp");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel adm");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel adm");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel operator");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel sync");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel shutdown");
	mysystem("/bin/chroot /harddisk /usr/sbin/userdel halt");
	mysystem("/bin/chroot /harddisk /usr/sbin/groupdel man");
	return 0;
}

void _del_pulsardsl_dir()
{
	mysystem("/bin/chroot /harddisk /bin/rm -rf " CONFIG_ROOT "/pulsardsl");
}

void _del_fritzdsl_dir()
{
	mysystem("/bin/chroot /harddisk /bin/rm -rf " CONFIG_ROOT "/fritzdsl");
}

int _convert_vpn() {
	int count=1;
	FILE *vpn1, *vpn2;
	char vpnip[STRING_SIZE] = "";
	char greennetaddr[STRING_SIZE] = "";
	struct keyvalue *kv = initkeyvalues();
	char vpnsrctemp[STRING_SIZE], vpndsttemp[STRING_SIZE];
	char *name, *left, *left_nexthop, *left_subnet, *right, *right_nexthop, *right_subnet, *secret, *enabled, *compression;

	if (!(vpn1 = fopen ("/harddisk" CONFIG_ROOT "/vpn/config", "r"))) return 1;
	if (!(vpn2 = fopen ("/harddisk" CONFIG_ROOT "/vpn/config.new", "w"))) 
	{
		fclose(vpn1);
		return 1;
	}

	if (!(readkeyvalues(kv, "/harddisk" CONFIG_ROOT "/ethernet/settings")))
	{
		fclose (vpn1);
		fclose (vpn2);
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	findkey(kv, "GREEN_NETADDRESS", greennetaddr);
	freekeyvalues(kv);

	kv = initkeyvalues();
	if (!(readkeyvalues(kv, "/harddisk" CONFIG_ROOT "/vpn/settings")))
	{
		fclose (vpn1);
		fclose (vpn2);
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}	
	
	/* if no VPN_IP is defined, we must turn it off to force the user
	 * to enter a value once upgraded */
	findkey(kv, "VPN_IP", vpnip);
	if (strlen(vpnip) == 0) {
		replacekeyvalue(kv, "ENABLED", "off");
		writekeyvalues(kv, "/harddisk" CONFIG_ROOT "/vpn/settings");
	}
	freekeyvalues(kv);

        while (fgets (vpnsrctemp, STRING_SIZE, vpn1) != NULL) {
		if (isdigit (vpnsrctemp[0])) {
			/* Already converted to new format */
			fputs(vpnsrctemp, vpn2);
			continue;
		}

		name          = NULL;
		left          = NULL;
		left_nexthop  = NULL;
		left_subnet   = NULL;
		right         = NULL;
		right_nexthop = NULL;
		right_subnet  = NULL;
		secret        = NULL;
		enabled       = NULL;
		compression   = NULL;
		
		if (vpnsrctemp[strlen(vpnsrctemp) - 1] == '\n')
			vpnsrctemp[strlen(vpnsrctemp) - 1] = '\0';
		name          = strtok (vpnsrctemp, ",");
		left          = strtok (NULL, ",");
		left_nexthop  = strtok (NULL, ",");
		left_subnet   = strtok (NULL, ",");
		right         = strtok (NULL, ",");
		right_nexthop = strtok (NULL, ",");
		right_subnet  = strtok (NULL, ",");
		secret        = strtok (NULL, ",");
		enabled       = strtok (NULL, ",");
		compression   = strtok (NULL, ",");
		if (!(name && left && left_subnet &&
			right && right_subnet &&
			secret && enabled && compression ))
			continue;

		/* Try and guess what side IPCop is on; defaults to left */
		if (strstr(greennetaddr, right_subnet)) {
			sprintf (vpndsttemp, "%d,%s,%s,,net,psk,%s,right,,%s,,%s,%s,,%s,,,,,,,,,,,,,RED\n",
							count, enabled, name, secret, right_subnet,
							left, left_subnet, compression);
		} else {
			sprintf (vpndsttemp, "%d,%s,%s,,net,psk,%s,left,,%s,,%s,%s,,%s,,,,,,,,,,,,,RED\n",
							count, enabled, name, secret, left_subnet,
							right, right_subnet, compression);
		}
		fputs(vpndsttemp, vpn2);

		count++;
	}

	/* Close source and destination vpn files */
	fclose (vpn1);
	fclose (vpn2);

	/* Move the new vpn file */
	rename ("/harddisk" CONFIG_ROOT "/vpn/config.new",
		"/harddisk" CONFIG_ROOT "/vpn/config");
	chown  ("/harddisk" CONFIG_ROOT "/vpn/config", 99, 99);

	return 0;
}

void _convert_ppp_settings_V140() {
	DIR *dirp;
	struct dirent *dp;
	char filename[STRING_SIZE];
	
	dirp = opendir( "/harddisk" CONFIG_ROOT "/ppp" );
	while ( (dp = readdir( dirp )) != NULL ) {
		if ( strstr( dp->d_name, "settings" ) == dp->d_name ) {
			snprintf (filename, STRING_SIZE-1, "%s/%s", 
				"/harddisk" CONFIG_ROOT "/ppp", dp->d_name);
			replace (filename, "PERSISTENT=on", "RECONNECTION=persistent");
			replace (filename, "DIALONDEMAND=on", "RECONNECTION=dialondemand");
			replace (filename, "MODULATION=GDTM", "MODULATION=GDMT");
			chown (filename, 99, 99);
		}	
	}
	(void) closedir( dirp );
}

void _convert_net_settings_V140(){
	replace ("/harddisk" CONFIG_ROOT "/ethernet/settings", "eepro100", "e100");
	chown   ("/harddisk" CONFIG_ROOT "/ethernet/settings", 99, 99);
}

void _convert_keymap() {
	replace("/harddisk" CONFIG_ROOT "/main/settings", "KEYMAP=/lib/kbd", "KEYMAP=/usr/share/kbd");
	replace("/harddisk" CONFIG_ROOT "/main/settings", ".kmap.gz", ".map.gz");
	chown  ("/harddisk" CONFIG_ROOT "/main/settings", 99, 99);
}

void _convert_speedtouch() {
	FILE *speedtchbootfile;
	FILE *speedtchfirmfile;

	if (( speedtchfirmfile = fopen ("/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v4.bin", "r")))
	{
		fclose (speedtchfirmfile);
		if  ((speedtchbootfile = fopen ("/harddisk" CONFIG_ROOT "/alcatelusb/boot.v4.bin", "r")))  {
			fclose (speedtchbootfile);
			system("/bin/cat /harddisk" CONFIG_ROOT "/alcatelusb/boot.v4.bin "
				"/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v4.bin"
				"> /harddisk" CONFIG_ROOT "/alcatelusb/firmware.v4_b.bin");
			remove ("/harddisk" CONFIG_ROOT "/alcatelusb/boot.v4.bin");
			remove ("/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v4.bin");
			chown ("/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v4_b.bin", 99, 99);
		}
	}

	if (( speedtchfirmfile = fopen ("/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v123.bin", "r"))) {
		fclose (speedtchfirmfile);
		system("/bin/cat /harddisk" CONFIG_ROOT "/alcatelusb/boot.v123.bin "
			"/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v123.bin"
			"> /harddisk" CONFIG_ROOT "/alcatelusb/firmware.v0123.bin");
		remove ("/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v123.bin");
	}

	remove ("/harddisk" CONFIG_ROOT "/alcatelusb/boot.v123.bin");

	rename ("/harddisk" CONFIG_ROOT "/alcatelusb/mgmt.o", "/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v0123.bin");
	chown ("/harddisk" CONFIG_ROOT "/alcatelusb/firmware.v0123.bin", 99, 99);
}

void _convert_isapnp() {
	FILE *isapnpfile;

	mkdir ("/harddisk" CONFIG_ROOT "/isapnp", S_IRWXU|S_IRWXG|S_IRWXO );
	if (( isapnpfile = fopen ("/harddisk/etc/isapnp.conf", "r"))) {
		fclose (isapnpfile);
		rename ("/harddisk/etc/isapnp.conf", "/harddisk" CONFIG_ROOT "/isapnp/isapnp.conf");
	} else {
		if (( isapnpfile = fopen ("/harddisk" CONFIG_ROOT "/isapnp/isapnp.conf", "r"))) {
			fclose(isapnpfile);
		} else {
			isapnpfile = fopen ("/harddisk" CONFIG_ROOT "/isapnp/isapnp.conf", "w");
			fclose(isapnpfile);
		}
	}
}

int upgrade_v130_v140() {
	_del_setup_user();
	_del_useless_user_group();
	_add_logwatch_user();
	_add_sshd_user();
	_add_dnsmasq_user();
	_add_cron_user();
	_add_sysklogd_user();
	_del_pulsardsl_dir();
	_del_fritzdsl_dir();
	_convert_vpn();
	_handledomainname();
	_fixsquid();
	_fixeagleusb();
	_create_nobody_dir();
	_convert_ppp_settings_V140();
	_convert_net_settings_V140();
	_fixdhcp_30();
	_convert_keymap();
	_convert_speedtouch();
	_convert_isapnp();

	return 0;
}
