#define _XOPEN_SOURCE 500
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <ftw.h>
#include "setuid.h"
#include "netutil.h"
#include "libsmooth.h"

#define noovpndebug

// global vars
	struct keyvalue *kv = NULL;
	FILE *ifacefile = NULL;

char redif[STRING_SIZE];
char blueif[STRING_SIZE];
char orangeif[STRING_SIZE];
char enablered[STRING_SIZE] = "off";
char enableblue[STRING_SIZE] = "off";
char enableorange[STRING_SIZE] = "off";

// consts
char OVPNINPUT[STRING_SIZE] = "OVPNINPUT";
char OVPNBLOCK[STRING_SIZE] = "OVPNBLOCK";
char OVPNNAT[STRING_SIZE] = "OVPNNAT";
char WRAPPERVERSION[STRING_SIZE] = "ipfire-2.2.4";

struct connection_struct {
	char name[STRING_SIZE];
	char type[STRING_SIZE];
	char proto[STRING_SIZE];
	char status[STRING_SIZE];
	char local_subnet[STRING_SIZE];
	char transfer_subnet[STRING_SIZE];
	char role[STRING_SIZE];
	char port[STRING_SIZE];
	struct connection_struct *next;
};

typedef struct connection_struct connection;

static int recursive_remove_callback(const char* fpath, const struct stat* sb, int typeflag, struct FTW* ftwbuf) {
	int rv = remove(fpath);
	if (rv)
		perror(fpath);

	return rv;
}

static int recursive_remove(const char* path) {
	return nftw(path, recursive_remove_callback, 64, FTW_DEPTH | FTW_PHYS);
}

void exithandler(void)
{
	if(kv)
		freekeyvalues(kv);
	if (ifacefile)
		fclose(ifacefile);
}

void usage(void)
{
#ifdef ovpndebug
	printf("Wrapper for OpenVPN %s-debug\n", WRAPPERVERSION);
#else
	printf("Wrapper for OpenVPN %s\n", WRAPPERVERSION);
#endif
	printf("openvpnctrl <option>\n");
	printf(" Valid options are:\n");
	printf(" -s   --start\n");
	printf("      starts OpenVPN (implicitly creates chains and firewall rules)\n");
	printf(" -k   --kill\n");
	printf("      kills/stops OpenVPN\n");
	printf(" -r   --restart\n");
	printf("      restarts OpenVPN (implicitly creates chains and firewall rules)\n");
	printf(" -sn2n --start-net-2-net\n");
	printf("      starts all net2net connections\n");
	printf("      you may pass a connection name to the switch to only start a specific one\n");
	printf(" -kn2n --kill-net-2-net\n");
	printf("      kills all net2net connections\n");
	printf("      you may pass a connection name to the switch to only start a specific one\n");
	printf(" -drrd --delete-rrd\n");
	printf("      Deletes the RRD data for a specific client\n");
	printf("      you need to pass a connection name (RW) to the switch to delete the directory (case sensitive)\n");
	printf(" -d   --display\n");
	printf("      displays OpenVPN status to syslog\n");
	printf(" -fwr --firewall-rules\n");
	printf("      removes current OpenVPN chains and rules and resets them according to the config\n");
	printf(" -sdo --start-daemon-only\n");
	printf("      starts OpenVPN daemon only\n");
	exit(1);
}

connection *getConnections() {
	FILE *fp = NULL;

	if (!(fp = fopen(CONFIG_ROOT "/ovpn/ovpnconfig", "r"))) {
		fprintf(stderr, "Could not open openvpn n2n configuration file.\n");
		exit(1);
	}

	char line[STRING_SIZE] = "";
	char result[STRING_SIZE] = "";
	char *resultptr;
	int count;
	connection *conn_first = NULL;
	connection *conn_last = NULL;
	connection *conn_curr;

	while ((fgets(line, STRING_SIZE, fp) != NULL)) {
		if (line[strlen(line) - 1] == '\n')
			line[strlen(line) - 1] = '\0';

		conn_curr = (connection *)malloc(sizeof(connection));
		memset(conn_curr, 0, sizeof(connection));

		if (conn_first == NULL) {
			conn_first = conn_curr;
		} else {
			conn_last->next = conn_curr;
		}
		conn_last = conn_curr;

		count = 0;
		char *lineptr = &line;
		while (1) {
			if (*lineptr == NULL)
				break;

			resultptr = result;
			while (*lineptr != NULL) {
				if (*lineptr == ',') {
					lineptr++;
					break;
				}
				*resultptr++ = *lineptr++;
			}
			*resultptr = '\0';

			if (count == 1) {
				strcpy(conn_curr->status, result);
			} else if (count == 2) {
				strcpy(conn_curr->name, result);
			} else if (count == 4) {
				strcpy(conn_curr->type, result);
			} else if (count == 7) {
				strcpy(conn_curr->role, result);
			} else if (count == 9) {
				strcpy(conn_curr->local_subnet, result);
			} else if (count == 28) {
				strcpy(conn_curr->transfer_subnet, result);
			} else if (count == 29) {
				strcpy(conn_curr->proto, result);
			} else if (count == 30) {
				strcpy(conn_curr->port, result);
			}

			count++;
		}
	}

	fclose(fp);

	return conn_first;
}

int readPidFile(const char *pidfile) {
	FILE *fp = fopen(pidfile, "r");
	if (fp == NULL) {
		exit(1);
	}

	int pid = 0;
	fscanf(fp, "%d", &pid);
	fclose(fp);

	return pid;
}

int readExternalAddress(char* address) {
	FILE *fp = fopen("/var/ipfire/red/local-ipaddress", "r");
	if (!fp)
		goto ERROR;

	int r = fscanf(fp, "%s", address);
	fclose(fp);

	if (r < 0)
		goto ERROR;

	/* In case the read IP address is not valid, we empty
	 * the content of address and return non-zero. */
	if (!VALID_IP(address))
		goto ERROR;

	return 0;

ERROR:
	address = NULL;
	return 1;
}

void ovpnInit(void) {
	// Read OpenVPN configuration
	kv = initkeyvalues();
	if (!readkeyvalues(kv, CONFIG_ROOT "/ovpn/settings")) {
		fprintf(stderr, "Cannot read ovpn settings\n");
		exit(1);
	}

	if (!findkey(kv, "ENABLED", enablered)) {
		exit(1);
	}

	if (!findkey(kv, "ENABLED_BLUE", enableblue)){
		exit(1);
	}

	if (!findkey(kv, "ENABLED_ORANGE", enableorange)){
		exit(1);
	}
	freekeyvalues(kv);

	// read interface settings

	// details for the red int
	memset(redif, 0, STRING_SIZE);
	if ((ifacefile = fopen(CONFIG_ROOT "/red/iface", "r")))
	{
		if (fgets(redif, STRING_SIZE, ifacefile))
		{
			if (redif[strlen(redif) - 1] == '\n')
				redif[strlen(redif) - 1] = '\0';
		}
		fclose (ifacefile);
		ifacefile = NULL;

		if (!VALID_DEVICE(redif))
		{
			memset(redif, 0, STRING_SIZE);
		}
	}

	kv=initkeyvalues();
	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")) {
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}

	if (strcmp(enableblue, "on") == 0) {
		if (!findkey(kv, "BLUE_DEV", blueif)) {
			exit(1);
		}
	}

	if (strcmp(enableorange, "on") == 0) {
		if (!findkey(kv, "ORANGE_DEV", orangeif)) {
			exit(1);
		}
	}
	freekeyvalues(kv);
}

void executeCommand(char *command) {
#ifdef ovpndebug
	printf(strncat(command, "\n", 2));
#endif
	safe_system(strncat(command, " >/dev/null 2>&1", 17));
}

void addRule(const char *chain, const char *interface, const char *protocol, const char *port) {
	char command[STRING_SIZE];

	snprintf(command, STRING_SIZE - 1, "/sbin/iptables -A %s -i %s -p %s --dport %s -j ACCEPT",
		chain, interface, protocol, port);
	executeCommand(command);
}

void flushChain(char *chain) {
	char str[STRING_SIZE];

	snprintf(str, STRING_SIZE - 1, "/sbin/iptables -F %s", chain);
	executeCommand(str);
}

void flushChainNAT(char *chain) {
	char str[STRING_SIZE];

	snprintf(str, STRING_SIZE - 1, "/sbin/iptables -t nat -F %s", chain);
	executeCommand(str);
}

char* calcTransferNetAddress(const connection* conn) {
	char *subnetmask = strdup(conn->transfer_subnet);
	char *address = strsep(&subnetmask, "/");

	if ((address == NULL) || (subnetmask == NULL)) {
		goto ERROR;
	}

	in_addr_t _address    = inet_addr(address);
	in_addr_t _subnetmask = inet_addr(subnetmask);
	_address &= _subnetmask;

	if (strcmp(conn->role, "server") == 0) {
		_address += 1 << 24;
	} else if (strcmp(conn->role, "client") == 0) {
		_address += 2 << 24;
	} else {
		goto ERROR;
	}

	struct in_addr address_info;
	address_info.s_addr = _address;

	return inet_ntoa(address_info);

ERROR:
	fprintf(stderr, "Could not determine transfer net address: %s\n", conn->name);

	free(address);
	return NULL;
}

char* getLocalSubnetAddress(const connection* conn) {
	kv = initkeyvalues();
	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")) {
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}

	const char *zones[] = {"GREEN", "BLUE", "ORANGE", NULL};
	char *zone = NULL;

	// Get net address of the local openvpn subnet.
	char *subnetmask = strdup(conn->local_subnet);
	char *address = strsep(&subnetmask, "/");

	if ((address == NULL) || (subnetmask == NULL)) {
		goto ERROR;
	}

	in_addr_t _address    = inet_addr(address);
	in_addr_t _subnetmask = inet_addr(subnetmask);

	in_addr_t _netaddr    = (_address &  _subnetmask);
	in_addr_t _broadcast  = (_address | ~_subnetmask);

	char zone_address_key[STRING_SIZE];
	char zone_address[STRING_SIZE];
	in_addr_t zone_addr;

	int i = 0;
	while (zones[i]) {
		zone = zones[i++];
		snprintf(zone_address_key, STRING_SIZE, "%s_ADDRESS", zone);

		if (!findkey(kv, zone_address_key, zone_address))
			continue;

		zone_addr = inet_addr(zone_address);
		if ((zone_addr > _netaddr) && (zone_addr < _broadcast)) {
			freekeyvalues(kv);

			return strdup(zone_address);
		}
	}

ERROR:
	fprintf(stderr, "Could not determine local subnet address: %s\n", conn->name);

	freekeyvalues(kv);
	return NULL;
}

void setFirewallRules(void) {
	char command[STRING_SIZE];
	char protocol[STRING_SIZE] = "";
	char dport[STRING_SIZE] = "";
	char dovpnip[STRING_SIZE] = "";

	kv = initkeyvalues();
	if (!readkeyvalues(kv, CONFIG_ROOT "/ovpn/settings"))
	{
		fprintf(stderr, "Cannot read ovpn settings\n");
		exit(1);
	}

	/* we got one device, so lets proceed further	*/
	if (!findkey(kv, "DDEST_PORT", dport)){
		fprintf(stderr, "Cannot read DDEST_PORT\n");
		exit(1);
	}

	if (!findkey(kv, "DPROTOCOL", protocol)){
		fprintf(stderr, "Cannot read DPROTOCOL\n");
		exit(1);
	}

	if (!findkey(kv, "VPN_IP", dovpnip)){
		fprintf(stderr, "Cannot read VPN_IP\n");
	}
	freekeyvalues(kv);

	// Flush all chains.
	flushChain(OVPNINPUT);
	flushChain(OVPNBLOCK);
	flushChainNAT(OVPNNAT);

	// set firewall rules
	if (!strcmp(enablered, "on") && strlen(redif))
		addRule(OVPNINPUT, redif, protocol, dport);
	if (!strcmp(enableblue, "on") && strlen(blueif))
		addRule(OVPNINPUT, blueif, protocol, dport);
	if (!strcmp(enableorange, "on") && strlen(orangeif))
		addRule(OVPNINPUT, orangeif, protocol, dport);

	/* Allow ICMP error messages to pass. */
	snprintf(command, STRING_SIZE - 1, "/sbin/iptables -A %s -p icmp"
		" -m conntrack --ctstate RELATED -j RETURN", OVPNBLOCK);
	executeCommand(command);

	// read connection configuration
	connection *conn = getConnections();

	// set firewall rules for n2n connections
	char *local_subnet_address = NULL;
	char *transfer_subnet_address = NULL;
	while (conn != NULL) {
		if (strcmp(conn->type, "net") == 0) {
			addRule(OVPNINPUT, redif, conn->proto, conn->port);

			/* Block all communication from the transfer nets. */
			snprintf(command, STRING_SIZE - 1, "/sbin/iptables -A %s -s %s -j DROP",
				OVPNBLOCK, conn->transfer_subnet);
			executeCommand(command);

			local_subnet_address = getLocalSubnetAddress(conn);
			transfer_subnet_address = calcTransferNetAddress(conn);

			if ((local_subnet_address) && (transfer_subnet_address)) {
				snprintf(command, STRING_SIZE - 1, "/sbin/iptables -t nat -A %s -s %s -j SNAT --to-source %s",
					OVPNNAT, transfer_subnet_address, local_subnet_address);
				executeCommand(command);
			}
		}

		conn = conn->next;
	}
}

static void stopAuthenticator() {
	const char* argv[] = {
		"/usr/sbin/openvpn-authenticator",
		NULL,
	};

	run("/sbin/killall", argv);
}

void stopDaemon(void) {
	char command[STRING_SIZE];

	int pid = readPidFile("/var/run/openvpn.pid");
	if (!pid > 0) {
		exit(1);
	}

	fprintf(stderr, "Killing PID %d.\n", pid);
	kill(pid, SIGTERM);

	snprintf(command, STRING_SIZE - 1, "/bin/rm -f /var/run/openvpn.pid");
	executeCommand(command);

	// Stop OpenVPN authenticator
	stopAuthenticator();
}

static int startAuthenticator(void) {
	const char* argv[] = { "-d", NULL };

	return run("/usr/sbin/openvpn-authenticator", argv);
}

void startDaemon(void) {
	char command[STRING_SIZE];

	if (!((strcmp(enablered, "on") == 0) || (strcmp(enableblue, "on") == 0) || (strcmp(enableorange, "on") == 0))) {
		fprintf(stderr, "OpenVPN is not enabled on any interface\n");
		exit(1);
	} else {
		snprintf(command, STRING_SIZE-1, "/etc/fcron.daily/openvpn-crl-updater");
		executeCommand(command);
		snprintf(command, STRING_SIZE-1, "/sbin/modprobe tun");
		executeCommand(command);
		snprintf(command, STRING_SIZE-1, "/usr/sbin/openvpn --config /var/ipfire/ovpn/server.conf");
		executeCommand(command);
		snprintf(command, STRING_SIZE-1, "/bin/chown root.nobody /var/run/ovpnserver.log");
		executeCommand(command);
		snprintf(command, STRING_SIZE-1, "/bin/chmod 644 /var/run/ovpnserver.log");
		executeCommand(command);

		// Start OpenVPN Authenticator
		startAuthenticator();
	}
}

int startNet2Net(char *name) {
	connection *conn = NULL;
	connection *conn_iter;

	conn_iter = getConnections();

	while (conn_iter) {
		if ((strcmp(conn_iter->type, "net") == 0) && (strcmp(conn_iter->name, name) == 0)) {
			conn = conn_iter;
			break;
		}
		conn_iter = conn_iter->next;
	}

	if (conn == NULL) {
		fprintf(stderr, "Connection not found.\n");
		return 1;
	}

	if (strcmp(conn->status, "on") != 0) {
		fprintf(stderr, "Connection '%s' is not enabled.\n", conn->name);
		return 1;
	}

	fprintf(stderr, "Starting connection %s...\n", conn->name);

	char configfile[STRING_SIZE];
	snprintf(configfile, STRING_SIZE - 1, CONFIG_ROOT "/ovpn/n2nconf/%s/%s.conf",
		conn->name, conn->name);

	FILE *fp = fopen(configfile, "r");
	if (fp == NULL) {
		fprintf(stderr, "Could not find configuration file for connection '%s' at '%s'.\n",
			conn->name, configfile);
		return 2;
	}
	fclose(fp);

	// Make sure all firewall rules are up to date.
	setFirewallRules();

	// Get the external IP address.
	char address[STRING_SIZE] = "";
	int r = readExternalAddress(address);
	if (r) {
		fprintf(stderr, "Could not read the external address\n");
		exit(1);
	}

	char command[STRING_SIZE];
	snprintf(command, STRING_SIZE-1, "/sbin/modprobe tun");
	executeCommand(command);
	snprintf(command, STRING_SIZE-1, "/usr/sbin/openvpn --local %s --config %s", address, configfile);
	executeCommand(command);

	return 0;
}

int killNet2Net(char *name) {
	connection *conn = NULL;
	connection *conn_iter;
	int rc = 0;

	conn_iter = getConnections();

	while (conn_iter) {
		if (strcmp(conn_iter->name, name) == 0) {
			conn = conn_iter;
			break;
		}
		conn_iter = conn_iter->next;
	}

	if (conn == NULL) {
		fprintf(stderr, "Connection not found.\n");
		return 1;
	}

	char pidfile[STRING_SIZE];
	snprintf(pidfile, STRING_SIZE - 1, "/var/run/%sn2n.pid", conn->name);

	int pid = readPidFile(pidfile);
	if (!pid > 0) {
		fprintf(stderr, "Could not read pid file of connection %s.", conn->name);
		return 1;
	}

	fprintf(stderr, "Killing connection %s (PID %d)...\n", conn->name, pid);
	kill(pid, SIGTERM);

	char command[STRING_SIZE];
	snprintf(command, STRING_SIZE - 1, "/bin/rm -f %s", pidfile);
	executeCommand(command);

	char runfile[STRING_SIZE];
	snprintf(runfile, STRING_SIZE - 1, "/var/run/openvpn/%s-n2n", conn->name);
	rc = recursive_remove(runfile);
	if (rc)
		perror(runfile);

	return 0;
}

int deleterrd(char *name) {
	char rrd_dir[STRING_SIZE];

	connection *conn = getConnections();
	while(conn) {
		if (strcmp(conn->name, name) != 0) {
			conn = conn->next;
			continue;
		}

		// Handle RW connections
		if (strcmp(conn->type, "host") == 0) {
			snprintf(rrd_dir, STRING_SIZE - 1, "/var/log/rrd/collectd/localhost/openvpn-%s/", name);

		// Handle N2N connections
		} else if (strcmp(conn->type, "net") == 0) {
			snprintf(rrd_dir, STRING_SIZE - 1, "/var/log/rrd/collectd/localhost/openvpn-%s-n2n/", name);

		// Unhandled connection type
		} else {
			conn = conn->next;
			continue;
		}

		return recursive_remove(rrd_dir);
	}

	return 1;
}

void startAllNet2Net() {
	int exitcode = 0, _exitcode = 0;

	connection *conn = getConnections();

	while(conn) {
		/* Skip all connections that are not of type "net" or disabled. */
		if ((strcmp(conn->type, "net") != 0) || (strcmp(conn->status, "on") != 0)) {
			conn = conn->next;
			continue;
		}

		_exitcode = startNet2Net(conn->name);
		conn = conn->next;

		if (_exitcode > exitcode) {
			exitcode = _exitcode;
		}
	}

	exit(exitcode);
}

void killAllNet2Net() {
	int exitcode = 0, _exitcode = 0;

	connection *conn = getConnections();

	while(conn) {
		/* Skip all connections that are not of type "net". */
		if (strcmp(conn->type, "net") != 0) {
			conn = conn->next;
			continue;
		}

		_exitcode = killNet2Net(conn->name);
		conn = conn->next;

		if (_exitcode > exitcode) {
			exitcode = _exitcode;
		}
	}

	exit(exitcode);
}

void displayopenvpn(void) {
	char command[STRING_SIZE];

	snprintf(command, STRING_SIZE - 1, "/bin/killall -sSIGUSR2 openvpn");
	executeCommand(command);
}

int main(int argc, char *argv[]) {
	if (!(initsetuid()))
	    exit(1);
	if(argc < 2)
	    usage();

	if(argc == 3) {
		ovpnInit();

		if( (strcmp(argv[1], "-sn2n") == 0) || (strcmp(argv[1], "--start-net-2-net") == 0) ) {
			startNet2Net(argv[2]);
			return 0;
		}
		else if( (strcmp(argv[1], "-kn2n") == 0) || (strcmp(argv[1], "--kill-net-2-net") == 0) ) {
			killNet2Net(argv[2]);
			return 0;
		}
		else if( (strcmp(argv[1], "-drrd") == 0) || (strcmp(argv[1], "--delete-rrd") == 0) ) {
			deleterrd(argv[2]);
			return 0;
		} else {
			usage();
			return 1;
		}
	}
	else if(argc == 2) {
		if( (strcmp(argv[1], "-k") == 0) || (strcmp(argv[1], "--kill") == 0) ) {
			stopDaemon();
			return 0;
		}
		else if( (strcmp(argv[1], "-d") == 0) || (strcmp(argv[1], "--display") == 0) ) {
			displayopenvpn();
			return 0;
		}
		else {
			ovpnInit();

			if( (strcmp(argv[1], "-s") == 0) || (strcmp(argv[1], "--start") == 0) ) {
				setFirewallRules();
				startDaemon();
				return 0;
			}
			else if( (strcmp(argv[1], "-sn2n") == 0) || (strcmp(argv[1], "--start-net-2-net") == 0) ) {
				startAllNet2Net();
				return 0;
			}
			else if( (strcmp(argv[1], "-kn2n") == 0) || (strcmp(argv[1], "--kill-net-2-net") == 0) ) {
				killAllNet2Net();
				return 0;
			}
			else if( (strcmp(argv[1], "-sdo") == 0) || (strcmp(argv[1], "--start-daemon-only") == 0) ) {
				startDaemon();
				return 0;
			}
			else if( (strcmp(argv[1], "-r") == 0) || (strcmp(argv[1], "--restart") == 0) ) {
				stopDaemon();
				setFirewallRules();
				startDaemon();
				return 0;
			}
			else if( (strcmp(argv[1], "-fwr") == 0) || (strcmp(argv[1], "--firewall-rules") == 0) ) {
				setFirewallRules();
				return 0;
			}
			else {
				usage();
				return 0;
			}
		}
	}
	else {
		usage();
		return 0;
	}
return 0;
}

