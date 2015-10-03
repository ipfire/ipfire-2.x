/*
 *
 * File originally from the Smoothwall project
 * (c) 2001 Smoothwall Team
 *
 */

#include "libsmooth.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>

#include "setuid.h"
#include "netutil.h"

/*
    This module is responsible for start stop of the vpn system.
    
    1) it allows AH & ESP to get in from interface where a vpn is mounted
        The NAT traversal is used on the udp 4500 port.

    2) it starts the ipsec daemon
        The RED interface is a problem because it can be up or down a startup.
        Then, the state change and it must not affect other VPN mounted on 
        other interface.
        Unfortunatly, openswan 1 cannot do that correctly. It cannot use an
        interface without restarting everything.

*/

void usage() {
        fprintf (stderr, "Usage:\n");
        fprintf (stderr, "\tipsecctrl S [connectionkey]\n");
        fprintf (stderr, "\tipsecctrl D [connectionkey]\n");
        fprintf (stderr, "\tipsecctrl R\n");
        fprintf (stderr, "\tipsecctrl I\n");
        fprintf (stderr, "\t\tS : Start/Restart Connection\n");
        fprintf (stderr, "\t\tD : Stop Connection\n");
        fprintf (stderr, "\t\tR : Reload Certificates and Secrets\n");
        fprintf (stderr, "\t\tI : Print Statusinfo\n");
}

static void ipsec_reload() {
	/* Re-read all configuration files and secrets and
	 * reload the daemon (#10339).
	 */
	safe_system("/usr/sbin/ipsec rereadall >/dev/null 2>&1");
	safe_system("/usr/sbin/ipsec reload >/dev/null 2>&1");
}

/*
        ACCEPT the ipsec protocol ah, esp & udp (for nat traversal) on the specified interface
*/
void open_physical (char *interface, int nat_traversal_port) {
        char str[STRING_SIZE];

        // IKE
        sprintf(str, "/sbin/iptables --wait -D IPSECINPUT -p udp -i %s --dport 500 -j ACCEPT >/dev/null 2>&1", interface);
        safe_system(str);
        sprintf(str, "/sbin/iptables --wait -A IPSECINPUT -p udp -i %s --dport 500 -j ACCEPT", interface);
        safe_system(str);

        if (! nat_traversal_port) 
            return;

        sprintf(str, "/sbin/iptables --wait -D IPSECINPUT -p udp -i %s --dport %i -j ACCEPT >/dev/null 2>&1", interface, nat_traversal_port);
        safe_system(str);
        sprintf(str, "/sbin/iptables --wait -A IPSECINPUT -p udp -i %s --dport %i -j ACCEPT", interface, nat_traversal_port);
        safe_system(str);
}

void ipsec_norules() {
        /* clear input rules */
        safe_system("/sbin/iptables --wait -F IPSECINPUT");
        safe_system("/sbin/iptables --wait -F IPSECFORWARD");
        safe_system("/sbin/iptables --wait -F IPSECOUTPUT");
}

/*
 return values from the vpn config file or false if not 'on'
*/
int decode_line (char *s, 
                char **key,
                char **name,
                char **type
                ) {
        int count = 0;
        *key = NULL;
        *name = NULL;
        *type = NULL;

        if (s[strlen(s) - 1] == '\n')
                s[strlen(s) - 1] = '\0';

        char *result = strsep(&s, ",");
        while (result) {
                if (count == 0)
                        *key = result;
                if ((count == 1) && strcmp(result, "on") != 0)
                        return 0;       // a disabled line
                if (count == 2)
                        *name = result;
                if (count == 4)
                        *type = result;
                count++;
                result = strsep(&s, ",");
        }

        // check other syntax
        if (! *name)
            return 0;
                        
        if (strspn(*name, LETTERS_NUMBERS) != strlen(*name)) {
                fprintf(stderr, "Bad connection name: %s\n", *name);
                return 0;
        }

        if (! (strcmp(*type, "host") == 0 || strcmp(*type, "net") == 0)) {
                fprintf(stderr, "Bad connection type: %s\n", *type);
                return 0;
        }

        //it's a valid & active line
        return 1;
}

/*
    issue ipsec commmands to turn on connection 'name'
*/
void turn_connection_on(char *name, char *type) {
	/*
	 * To bring up a connection, we need to reload the configuration
	 * and issue ipsec up afterwards. To make sure the connection
	 * is not established from the start, we bring it down in advance.
	 */
        char command[STRING_SIZE];

	// Bring down the connection (if established).
        snprintf(command, STRING_SIZE - 1, 
                "/usr/sbin/ipsec down %s >/dev/null", name);
        safe_system(command);

	// Reload the IPsec block chain
	safe_system("/usr/lib/firewall/ipsec-block >/dev/null");

	// Reload the configuration into the daemon (#10339).
	ipsec_reload();

	// Bring the connection up again.
	snprintf(command, STRING_SIZE - 1,
		"/usr/sbin/ipsec up %s >/dev/null", name);
	safe_system(command);
}

/*
    issue ipsec commmands to turn off connection 'name'
*/
void turn_connection_off (char *name) {
	/*
	 * To turn off a connection, all SAs must be turned down.
	 * After that, the configuration must be reloaded.
	 */
        char command[STRING_SIZE];

	// Bring down the connection.
        snprintf(command, STRING_SIZE - 1, 
                "/usr/sbin/ipsec down %s >/dev/null", name);
        safe_system(command);

	// Reload, so the connection is dropped.
	ipsec_reload();
}

int main(int argc, char *argv[]) {
        char configtype[STRING_SIZE];
        char redtype[STRING_SIZE] = "";
        struct keyvalue *kv = NULL;
                        
        if (argc < 2) {
                usage();
                exit(1);
        }
        if (!(initsetuid()))
                exit(1);
                
 FILE *file = NULL;
                

        if (strcmp(argv[1], "I") == 0) {
                safe_system("/usr/sbin/ipsec status");
                exit(0);
        }

        if (strcmp(argv[1], "R") == 0) {
		ipsec_reload();
                exit(0);
        }

        /* FIXME: workaround for pclose() issue - still no real idea why
         * this is happening */
        signal(SIGCHLD, SIG_DFL);

        /* handle operations that doesn't need start the ipsec system */
        if (argc == 2) {
                if (strcmp(argv[1], "D") == 0) {
                        safe_system("/usr/sbin/ipsec stop >/dev/null 2>&1");
                        ipsec_norules();
                        exit(0);
                }
        }

        /* read vpn config */
        kv=initkeyvalues();
        if (!readkeyvalues(kv, CONFIG_ROOT "/vpn/settings"))
        {
                fprintf(stderr, "Cannot read vpn settings\n");
                exit(1);
        }

        /* check is the vpn system is enabled */
        {
            char s[STRING_SIZE];
            findkey(kv, "ENABLED", s);
            freekeyvalues(kv);
            if (strcmp (s, "on") != 0)
                exit(0);
        }

        /* read interface settings */
        kv=initkeyvalues();
        if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings"))
        {
                fprintf(stderr, "Cannot read ethernet settings\n");
                exit(1);
        }
        if (!findkey(kv, "CONFIG_TYPE", configtype))
        {
                fprintf(stderr, "Cannot read CONFIG_TYPE\n");
                exit(1);
        }
        findkey(kv, "RED_TYPE", redtype);


        /* Loop through the config file to find physical interface that will accept IPSEC */
        int enable_red=0;       // states 0: not used
        int enable_green=0;     //        1: error condition
        int enable_orange=0;    //        2: good
        int enable_blue=0;
        char if_red[STRING_SIZE] = "";
        char if_green[STRING_SIZE] = "";
        char if_orange[STRING_SIZE] = "";
        char if_blue[STRING_SIZE] = "";
        char s[STRING_SIZE];

        // when RED is up, find interface name in special file
        FILE *ifacefile = NULL;
        if ((ifacefile = fopen(CONFIG_ROOT "/red/iface", "r"))) {
                if (fgets(if_red, STRING_SIZE, ifacefile)) {
                        if (if_red[strlen(if_red) - 1] == '\n')
                                if_red[strlen(if_red) - 1] = '\0';
                }
                fclose (ifacefile);

                if (VALID_DEVICE(if_red))
                        enable_red++;
        }

	// Check if GREEN is enabled.
        findkey(kv, "GREEN_DEV", if_green);
        if (VALID_DEVICE(if_green))
                enable_green++;

	// Check if ORANGE is enabled.
        findkey(kv, "ORANGE_DEV", if_orange);
        if (VALID_DEVICE(if_orange))
                enable_orange++;

	// Check if BLUE is enabled.
        findkey(kv, "BLUE_DEV", if_blue);
        if (VALID_DEVICE(if_blue))
                enable_blue++;

        freekeyvalues(kv);

        // exit if nothing to do
        if ((enable_red+enable_green+enable_orange+enable_blue) == 0)
            exit(0);

        // open needed ports
        if (enable_red > 0)
                open_physical(if_red, 4500);

        if (enable_green > 0)
                open_physical(if_green, 4500);

        if (enable_orange > 0)
                open_physical(if_orange, 4500);

        if (enable_blue > 0)
                open_physical(if_blue, 4500);

        // start the system
        if ((argc == 2) && strcmp(argv[1], "S") == 0) {
		safe_system("/usr/lib/firewall/ipsec-block >/dev/null");
		safe_system("/usr/sbin/ipsec restart >/dev/null");
                exit(0);
        }

        // it is a selective start or stop
        // second param is only a number 'key'
        if ((argc == 2) || strspn(argv[2], NUMBERS) != strlen(argv[2])) {
                fprintf(stderr, "Bad arg: %s\n", argv[2]);
                usage();
                exit(1);
        }

        // search the vpn pointed by 'key'
        if (!(file = fopen(CONFIG_ROOT "/vpn/config", "r"))) {
                fprintf(stderr, "Couldn't open vpn settings file");
                exit(1);
        }
        while (fgets(s, STRING_SIZE, file) != NULL) {
                char *key;
                char *name;
                char *type;
                if (!decode_line(s,&key,&name,&type))
                        continue;

                // is it the 'key' requested ?
                if (strcmp(argv[2], key) != 0)
                        continue;

                // Start or Delete this Connection
                if (strcmp(argv[1], "S") == 0)
                        turn_connection_on (name, type);
                else if (strcmp(argv[1], "D") == 0)
                        turn_connection_off (name);
                else {
                        fprintf(stderr, "Bad command\n");
                        exit(1);
                }
        }
        fclose(file);

        return 0;
}
