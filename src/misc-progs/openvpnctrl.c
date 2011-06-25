#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <fcntl.h>
#include "setuid.h"
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
char OVPNRED[STRING_SIZE] = "OVPN";
char OVPNBLUE[STRING_SIZE] = "OVPN_BLUE_";
char OVPNORANGE[STRING_SIZE] = "OVPN_ORANGE_";
char WRAPPERVERSION[STRING_SIZE] = "ipfire-2.1.1";

struct connection_struct {
	char name[STRING_SIZE];
	char proto[STRING_SIZE];
	int port;
	struct connection_struct *next;
};

typedef struct connection_struct connection;

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
	printf(" -d   --display\n");
	printf("      displays OpenVPN status to syslog\n");
	printf(" -fwr --firewall-rules\n");
	printf("      removes current OpenVPN chains and rules and resets them according to the config\n");
	printf(" -sdo --start-daemon-only\n");
	printf("      starts OpenVPN daemon only\n");
	printf(" -ccr --create-chains-and-rules\n");
	printf("      creates chains and rules for OpenVPN\n");
	printf(" -dcr --delete-chains-and-rules\n");
	printf("      removes all chains for OpenVPN\n");
	exit(1);
}

connection *getConnections() {
	FILE *fp = NULL;

	if (!(fp = fopen(CONFIG_ROOT "/ovpn/ovpnconfig", "r"))) {
		fprintf(stderr, "Could not open openvpn n2n configuration file.\n");
		exit(1);
	}

	char line[STRING_SIZE] = "";
	char *result;
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
		result = strtok(line, ",");
		while (result) {
			if (count == 2) {
				strcpy(conn_curr->name, result);
			} else if (count == 12) {
				strcpy(conn_curr->proto, result);
			} else if (count == 13) {
				conn_curr->port = atoi(result);
			}

			result = strtok(NULL, ",");
			count++;
		}
	}

	fclose(fp);

	return conn_first;
}

void ovpnInit(void) {
	
	// Read OpenVPN configuration
	kv = initkeyvalues();
	if (!readkeyvalues(kv, CONFIG_ROOT "/ovpn/settings")) {
		fprintf(stderr, "Cannot read ovpn settings\n");
		exit(1);
	}

	if (!findkey(kv, "ENABLED", enablered)) {
		fprintf(stderr, "Cannot read ENABLED\n");
		exit(1);
	}

	if (!findkey(kv, "ENABLED_BLUE", enableblue)){
		fprintf(stderr, "Cannot read ENABLED_BLUE\n");
		exit(1);
	}

	if (!findkey(kv, "ENABLED_ORANGE", enableorange)){
		fprintf(stderr, "Cannot read ENABLED_ORANGE\n");
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
	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings"))
	{
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}
	
	if (strcmp(enableblue, "on")==0){
		if (!findkey(kv, "BLUE_DEV", blueif)){
			fprintf(stderr, "Cannot read BLUE_DEV\n");
			exit(1);
		}
	}
	if (strcmp(enableorange, "on")==0){
		if (!findkey(kv, "ORANGE_DEV", orangeif)){
			fprintf(stderr, "Cannot read ORNAGE_DEV\n");
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

void setChainRules(char *chain, char *interface, char *protocol, char *port)
{
	char str[STRING_SIZE];

	sprintf(str, "/sbin/iptables -A %sINPUT -i %s -p %s --dport %s -j ACCEPT", chain, interface, protocol, port);
	executeCommand(str);
	sprintf(str, "/sbin/iptables -A %sINPUT -i tun+ -j ACCEPT", chain);
	executeCommand(str);
	sprintf(str, "/sbin/iptables -A %sFORWARD -i tun+ -j ACCEPT", chain);
	executeCommand(str);
}

void flushChain(char *chain) {
	char str[STRING_SIZE];

	sprintf(str, "/sbin/iptables -F %sINPUT", chain);
	executeCommand(str);
	sprintf(str, "/sbin/iptables -F %sFORWARD", chain);
	executeCommand(str);
	safe_system(str);
}

void deleteChainReference(char *chain) {
	char str[STRING_SIZE];

	sprintf(str, "/sbin/iptables -D INPUT -j %sINPUT", chain);
	executeCommand(str);
	safe_system(str);
	sprintf(str, "/sbin/iptables -D FORWARD -j %sFORWARD", chain);
	executeCommand(str);
	safe_system(str);
}

void deleteChain(char *chain) {
	char str[STRING_SIZE];

	sprintf(str, "/sbin/iptables -X %sINPUT", chain);
	executeCommand(str);
	sprintf(str, "/sbin/iptables -X %sFORWARD", chain);
	executeCommand(str);
}

void deleteAllChains(void) {
	// not an elegant solution, but to avoid timing problems with undeleted chain references
	deleteChainReference(OVPNRED);
	deleteChainReference(OVPNBLUE);
	deleteChainReference(OVPNORANGE);
	flushChain(OVPNRED);
	flushChain(OVPNBLUE);
	flushChain(OVPNORANGE);
	deleteChain(OVPNRED);
	deleteChain(OVPNBLUE);
	deleteChain(OVPNORANGE);
}

void createChainReference(char *chain) {
	char str[STRING_SIZE];
	sprintf(str, "/sbin/iptables -I INPUT %s -j %sINPUT", "14", chain);
	executeCommand(str);
	sprintf(str, "/sbin/iptables -I FORWARD %s -j %sFORWARD", "12", chain);
	executeCommand(str);
}

void createChain(char *chain) {
	char str[STRING_SIZE];
	sprintf(str, "/sbin/iptables -N %sINPUT", chain);
	executeCommand(str);
	sprintf(str, "/sbin/iptables -N %sFORWARD", chain);
	executeCommand(str);
}

void createAllChains(void) {
	if (!((strcmp(enablered, "on")==0) || (strcmp(enableblue, "on")==0) || (strcmp(enableorange, "on")==0))){
		fprintf(stderr, "OpenVPN is not enabled on any interface\n");
		exit(1);
	} else {
		// create chain and chain references
		if (!strcmp(enableorange, "on")) {
			if (strlen(orangeif)) {
				createChain(OVPNORANGE);
				createChainReference(OVPNORANGE);
			} else {
				fprintf(stderr, "OpenVPN enabled on orange but no orange interface found\n");
				//exit(1);
			}
		}
	
		if (!strcmp(enableblue, "on")) {
			if (strlen(blueif)) {
				createChain(OVPNBLUE);
				createChainReference(OVPNBLUE);
			} else {
				fprintf(stderr, "OpenVPN enabled on blue but no blue interface found\n");
				//exit(1);
			}
		}
	
		if (!strcmp(enablered, "on")) {
			if (strlen(redif)) {
				createChain(OVPNRED);
				createChainReference(OVPNRED);
			} else {
				fprintf(stderr, "OpenVPN enabled on red but no red interface found\n");
				//exit(1);
			}
		}
	}
}

void setFirewallRules(void) {
	char protocol[STRING_SIZE] = "";
	char dport[STRING_SIZE] = "";
	char dovpnip[STRING_SIZE] = "";

	/* check if it makes sence to proceed further */
	if (!((strcmp(enablered, "on")==0) || (strcmp(enableblue, "on")==0) || (strcmp(enableorange, "on")==0))){
		fprintf(stderr, "Config error, at least one device must be enabled\n");
		exit(1);
	}

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
//		exit(1); step further as we don't need an ip
	}
	freekeyvalues(kv);

	// read connection configuration
	connection *conn = getConnections();

	// Flush all chains.
	flushChain(OVPNRED);
	flushChain(OVPNBLUE);
	flushChain(OVPNORANGE);

	// set firewall rules
	if (!strcmp(enablered, "on") && strlen(redif))
		setChainRules(OVPNRED, redif, protocol, dport);
	if (!strcmp(enableblue, "on") && strlen(blueif))
		setChainRules(OVPNBLUE, blueif, protocol, dport);
	if (!strcmp(enableorange, "on") && strlen(orangeif))
		setChainRules(OVPNORANGE, orangeif, protocol, dport);

	// set firewall rules for n2n connections
	char *port;
	while (conn) {
		sprintf(port, "%d", conn->port);
		setChainRules(OVPNRED, redif, conn->proto, port);
		conn = conn->next;
	}
}

void stopDaemon(void) {
	char command[STRING_SIZE];

	snprintf(command, STRING_SIZE - 1, "/bin/killall openvpn");
	executeCommand(command);
	snprintf(command, STRING_SIZE - 1, "/bin/rm -f /var/run/openvpn.pid");
	executeCommand(command);
	snprintf(command, STRING_SIZE-1, "/sbin/modprobe -r tun");
	executeCommand(command);
}

void startDaemon(void) {
	char command[STRING_SIZE];
	
	if (!((strcmp(enablered, "on")==0) || (strcmp(enableblue, "on")==0) || (strcmp(enableorange, "on")==0))){
		fprintf(stderr, "OpenVPN is not enabled on any interface\n");
		exit(1);
	} else {
		snprintf(command, STRING_SIZE-1, "/sbin/modprobe tun");
		executeCommand(command);
		snprintf(command, STRING_SIZE-1, "/usr/sbin/openvpn --config /var/ipfire/ovpn/server.conf");
		executeCommand(command);
	}
}

void startNet2Net(char *name) {
	connection *conn = NULL;
	connection *conn_iter;

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
		exit(1);
	}

	// Make sure all firewall rules are up to date.
	setFirewallRules();

	char command[STRING_SIZE];
	sprintf(command, "/usr/sbin/openvpn --config " CONFIG_ROOT "/ovpn/n2nconf/%s/%s.conf", conn->name, conn->name);
	executeCommand(command);
}

void killNet2Net(char *conn) {
	printf("TO BE DONE %s\n", conn);
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
		if( (strcmp(argv[1], "-sn2n") == 0) || (strcmp(argv[1], "--start-net-2-net") == 0) ) {
			startNet2Net(argv[2]);
			return 0;
		}
		else if( (strcmp(argv[1], "-kn2n") == 0) || (strcmp(argv[1], "--kill-net-2-net") == 0) ) {
			killNet2Net(argv[2]);
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
		else if( (strcmp(argv[1], "-dcr") == 0) || (strcmp(argv[1], "--delete-chains-and-rules") == 0) ) {
			deleteAllChains();
			return 0;
		}
		else {
			ovpnInit();
			
			if( (strcmp(argv[1], "-s") == 0) || (strcmp(argv[1], "--start") == 0) ) {
				deleteAllChains();
				createAllChains();
				setFirewallRules();
				startDaemon();
				return 0;
			}
			else if( (strcmp(argv[1], "-sdo") == 0) || (strcmp(argv[1], "--start-daemon-only") == 0) ) {
				startDaemon();
				return 0;
			}
			else if( (strcmp(argv[1], "-r") == 0) || (strcmp(argv[1], "--restart") == 0) ) {
				stopDaemon();
				deleteAllChains();
				createAllChains();
				setFirewallRules();
				startDaemon();
				return 0;
			}
			else if( (strcmp(argv[1], "-fwr") == 0) || (strcmp(argv[1], "--firewall-rules") == 0) ) {
				deleteAllChains();
				createAllChains();
				setFirewallRules();
				return 0;
			}
			else if( (strcmp(argv[1], "-ccr") == 0) || (strcmp(argv[1], "--create-chains-and-rules") == 0) ) {
				createAllChains();
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

