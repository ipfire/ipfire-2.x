/* This file is part of the IPFire Firewall.
*
* This program is distributed under the terms of the GNU General Public
* Licence.  See the file COPYING for details. */

#define _BSD_SOURCE
#define _XOPEN_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "libsmooth.h"
#include "setuid.h"

#define CAPTIVE_PORTAL_SETTINGS		CONFIG_ROOT "/captive/settings"
#define ETHERNET_SETTINGS		CONFIG_ROOT "/ethernet/settings"

#define CLIENTS				CONFIG_ROOT "/captive/clients"
#define IPTABLES			"/sbin/iptables --wait"
#define HTTP_PORT			80
#define REDIRECT_PORT			1013

typedef struct client {
	char etheraddr[STRING_SIZE];
	char ipaddr[STRING_SIZE];
	time_t time_start;
	int expires;

	struct client* next;
} client_t;

static time_t parse_time(const char* s) {
	int t = 0;

	if (sscanf(s, "%d", &t) == 1) {
		return (time_t)t;
	}

	return -1;
}

static char* format_time(const time_t* t) {
	char buffer[STRING_SIZE];

	struct tm* tm = gmtime(t);
	if (tm == NULL)
		return NULL;

	strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M", tm);

	return strdup(buffer);
}

static client_t* read_clients(char* filename) {
	FILE* f = NULL;

	if (!(f = fopen(filename, "r"))) {
		fprintf(stderr, "Could not open configuration file: %s\n", filename);
		return NULL;;
	}

	char line[STRING_SIZE];

	client_t* client_first = NULL;
	client_t* client_last = NULL;
	client_t* client_curr;

	while ((fgets(line, STRING_SIZE, f) != NULL)) {
		if (line[strlen(line) - 1] == '\n')
			line[strlen(line) - 1] = '\0';

		// Skip all commented lines
		if (*line == '#')
			continue;

		client_curr = (client_t*)malloc(sizeof(client_t));
		memset(client_curr, 0, sizeof(client_t));

		if (client_first == NULL)
			client_first = client_curr;
		else
			client_last->next = client_curr;
		client_last = client_curr;

		unsigned int count = 0;
		char* lineptr = line;
		while (1) {
			if (!*lineptr)
				break;

			char* word = lineptr;
			while (*lineptr != '\0') {
				if (*lineptr == ',') {
					*lineptr = '\0';
					lineptr++;
					break;
				}
				lineptr++;
			}

			switch (count++) {
				// Ethernet address
				case 1:
					strcpy(client_curr->etheraddr, word);
					break;

				// IP address
				case 2:
					strcpy(client_curr->ipaddr, word);
					break;

				// Start time
				case 3:
					client_curr->time_start = parse_time(word);
					break;

				// Expire duration
				case 4:
					client_curr->expires = atoi(word);
					break;

				default:
					break;
			}
		}
	}

	if (f)
		fclose(f);

	return client_first;
}

static void flush_chains() {
	// filter
	safe_system(IPTABLES " -F CAPTIVE_PORTAL");
	safe_system(IPTABLES " -F CAPTIVE_PORTAL_CLIENTS");

	// nat
	safe_system(IPTABLES " -t nat -F CAPTIVE_PORTAL");
}

static int setup_dns_filters() {
	const char* protos[] = { "udp", "tcp", NULL };

	// Limits the number of DNS requests to 3 kByte/s
	// A burst of 1MB is permitted at the start
	const char* limiter = "-m hashlimit --hashlimit-name dns-filter"
		" --hashlimit-mode srcip --hashlimit-upto 3kb/sec --hashlimit-burst 1024kb";

	char command[STRING_SIZE];

	const char** proto = protos;
	while (*proto) {
		snprintf(command, sizeof(command), IPTABLES " -A CAPTIVE_PORTAL_CLIENTS -p %s"
			" --dport 53 %s -j RETURN", *proto, limiter);

		int r = safe_system(command);
		if (r)
			return r;

		proto++;
	}

	return 0;
}

static int add_client_rules(const client_t* clients) {
	char command[STRING_SIZE];
	char match[STRING_SIZE];

	while (clients) {
		size_t len = 0;

		if (*clients->ipaddr && clients->expires > 0) {
			len += snprintf(match + len, sizeof(match) - len,
				"-s %s", clients->ipaddr);
		}

		len += snprintf(match + len, sizeof(match) - len,
			" -m mac --mac-source %s", clients->etheraddr);

		if (clients->expires > 0) {
			time_t expires = clients->time_start + clients->expires;

			char* time_start = format_time(&clients->time_start);
			char* time_end = format_time(&expires);

			len += snprintf(match + len, sizeof(match) - len,
				" -m time --datestart %s --datestop %s",
				time_start, time_end);

			free(time_start);
			free(time_end);
		}

		// filter
		snprintf(command, sizeof(command), IPTABLES " -A CAPTIVE_PORTAL_CLIENTS"
			" %s -j RETURN", match);
		safe_system(command);

		// nat
		snprintf(command, sizeof(command), IPTABLES " -t nat -A CAPTIVE_PORTAL"
			" %s -j RETURN", match);
		safe_system(command);

		// Move on to the next client
		clients = clients->next;
	}

	return 0;
}

static char* get_key(struct keyvalue* settings, char* key) {
	char value[STRING_SIZE];

	if (!findkey(settings, key, value))
		return NULL;

	return strdup(value);
}

static int add_interface_rule(const char* intf, int allow_webif_access) {
	int r;
	char command[STRING_SIZE];

	if ((intf == NULL) || (strlen(intf) == 0)) {
		fprintf(stderr, "Empty interface given\n");
		return -1;
	}

	snprintf(command, sizeof(command), IPTABLES " -A CAPTIVE_PORTAL -i %s"
		" -j CAPTIVE_PORTAL_CLIENTS", intf);
	r = safe_system(command);
	if (r)
		return r;

	if (allow_webif_access) {
		snprintf(command, sizeof(command), IPTABLES " -A CAPTIVE_PORTAL_CLIENTS"
			" -i %s -p tcp --dport 444 -j RETURN", intf);
		r = safe_system(command);
		if (r)
			return r;
	}

	// Redirect all unauthenticated clients
	snprintf(command, sizeof(command), IPTABLES " -t nat -A CAPTIVE_PORTAL -i %s"
		" -p tcp --dport %d -j REDIRECT --to-ports %d", intf, HTTP_PORT, REDIRECT_PORT);
	r = safe_system(command);
	if (r)
		return r;

	// Allow access to captive portal site
	snprintf(command, sizeof(command), IPTABLES " -A CAPTIVE_PORTAL_CLIENTS"
		" -i %s -p tcp --dport %d -j RETURN", intf, REDIRECT_PORT);
	r = safe_system(command);
	if (r)
		return r;

	return 0;
}

static int add_interface_rules(struct keyvalue* captive_portal_settings, struct keyvalue* ethernet_settings) {
	const char* intf;
	char* setting;
	int r = 0;

	setting = get_key(captive_portal_settings, "ENABLE_GREEN");
	if (setting && (strcmp(setting, "on") == 0)) {
		free(setting);

		intf = get_key(ethernet_settings, "GREEN_DEV");
		r = add_interface_rule(intf, /* allow webif access from green */ 1);
		if (r)
			return r;
	}

	setting = get_key(captive_portal_settings, "ENABLE_BLUE");
	if (setting && (strcmp(setting, "on") == 0)) {
		free(setting);

		intf = get_key(ethernet_settings, "BLUE_DEV");
		r = add_interface_rule(intf, /* do not allow webif access */ 0);
		if (r)
			return r;
	}

	// Always pass DNS packets through all firewall rules
	r = setup_dns_filters();
	if (r)
		return r;

	// Add the last rule
	r = safe_system(IPTABLES " -A CAPTIVE_PORTAL_CLIENTS -j DROP");
	if (r)
		return r;

	return r;
}

int main(int argc, char** argv) {
	int r = 0;
	char* intf = NULL;
	client_t* clients = NULL;

	struct keyvalue* captive_portal_settings = NULL;
	struct keyvalue* ethernet_settings = NULL;

	if (!(initsetuid()))
		exit(2);

	ethernet_settings = initkeyvalues();
	if (!readkeyvalues(ethernet_settings, ETHERNET_SETTINGS)) {
		fprintf(stderr, "Could not read %s\n", ETHERNET_SETTINGS);
		r = 1;
		goto END;
	}

	captive_portal_settings = initkeyvalues();
	if (!readkeyvalues(captive_portal_settings, CAPTIVE_PORTAL_SETTINGS)) {
		fprintf(stderr, "Could not read %s\n", CAPTIVE_PORTAL_SETTINGS);
		r = 1;
		goto END;
	}

	clients = read_clients(CLIENTS);

	// Clean up all old rules
	flush_chains();

	// Add all client rules
	r = add_client_rules(clients);
	if (r)
		goto END;

	// Add all interface rules
	r = add_interface_rules(captive_portal_settings, ethernet_settings);
	if (r)
		goto END;

END:
	while (clients) {
		client_t* head = clients;
		clients = clients->next;

		free(head);
	}

	if (ethernet_settings)
		freekeyvalues(ethernet_settings);

	if (captive_portal_settings)
		freekeyvalues(captive_portal_settings);

	if (intf)
		free(intf);

	return r;
}
