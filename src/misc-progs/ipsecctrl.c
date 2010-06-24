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

/*
        ACCEPT the ipsec protocol ah, esp & udp (for nat traversal) on the specified interface
*/
void open_physical (char *interface, int nat_traversal_port) {
        char str[STRING_SIZE];

        // GRE ???
//        sprintf(str, "/sbin/iptables -A " phystable " -p 47  -i %s -j ACCEPT", interface);
//        safe_system(str);
        // ESP
//        sprintf(str, "/sbin/iptables -A " phystable " -p 50  -i %s -j ACCEPT", interface);
//        safe_system(str);
        // AH
//        sprintf(str, "/sbin/iptables -A " phystable " -p 51  -i %s -j ACCEPT", interface);
//        safe_system(str);
        // IKE

        sprintf(str, "/sbin/iptables -D IPSECINPUT -p udp -i %s --sport 500 --dport 500 -j ACCEPT >/dev/null 2>&1", interface);
        safe_system(str);
        sprintf(str, "/sbin/iptables -A IPSECINPUT -p udp -i %s --sport 500 --dport 500 -j ACCEPT", interface);
        safe_system(str);

        if (! nat_traversal_port) 
            return;

        sprintf(str, "/sbin/iptables -D IPSECINPUT -p udp -i %s --dport %i -j ACCEPT >/dev/null 2>&1", interface, nat_traversal_port);
        safe_system(str);
        sprintf(str, "/sbin/iptables -A IPSECINPUT -p udp -i %s --dport %i -j ACCEPT", interface, nat_traversal_port);
        safe_system(str);
}

void ipsec_norules() {
        /* clear input rules */
        safe_system("/sbin/iptables -F IPSECINPUT");
        safe_system("/sbin/iptables -F IPSECFORWARD");
        safe_system("/sbin/iptables -F IPSECOUTPUT");

}

/*
 return values from the vpn config file or false if not 'on'
*/
int decode_line (char *s, 
                char **key,
                char **name,
                char **type,
                char **interface
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
                if (count == 27)
                        *interface = result;
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

        if (! (strcmp(*interface, "RED") == 0 || strcmp(*interface, "GREEN") == 0 ||
                strcmp(*interface, "ORANGE") == 0 || strcmp(*interface, "BLUE") == 0)) {
                fprintf(stderr, "Bad interface name: %s\n", *interface);
                return 0;
        }
        //it's a valid & active line
        return 1;
}

/*
    issue ipsec commmands to turn on connection 'name'
*/
void turn_connection_on (char *name, char *type) {
        char command[STRING_SIZE];

        safe_system("/usr/sbin/ipsec reload >/dev/null");
        memset(command, 0, STRING_SIZE);
        /* give ipsec time to be ready */
        safe_system("/bin/sleep 5");
        snprintf(command, STRING_SIZE - 1, 
                "/usr/sbin/ipsec up %s >/dev/null", name);
        safe_system(command);
}
/*
    issue ipsec commmands to turn off connection 'name'
*/
void turn_connection_off (char *name) {
        char command[STRING_SIZE];
        memset(command, 0, STRING_SIZE);
        snprintf(command, STRING_SIZE - 1, 
                "/usr/sbin/ipsec whack --delete --name %s >/dev/null", name);
        safe_system(command);
        safe_system("/usr/sbin/ipsec whack --rereadall >/dev/null");
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
                safe_system("/usr/sbin/ipsec whack --status");
                exit(0);
        }

        if (strcmp(argv[1], "R") == 0) {
                safe_system("/usr/sbin/ipsec whack --rereadall >/dev/null");
                exit(0);
        }

 /* Get vpnwatch pid */

 if ( (argc == 2) && (file = fopen("/var/run/vpn-watch.pid", "r"))) {
 safe_system("kill -9 $(cat /var/run/vpn-watch.pid)");
 safe_system("unlink /var/run/vpn-watch.pid");
 close(file);
 }
 
        /* FIXME: workaround for pclose() issue - still no real idea why
         * this is happening */
        signal(SIGCHLD, SIG_DFL);

        /* handle operations that doesn't need start the ipsec system */
        if (argc == 2) {
                if (strcmp(argv[1], "D") == 0) {
                        /* Only shutdown pluto if it really is running */
                        /* Get pluto pid */
                        if (file = fopen("/var/run/pluto.pid", "r")) {
                                safe_system("/etc/rc.d/init.d/ipsec stop 2> /dev/null >/dev/null");
                                close(file);
                        }
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

        if (!(file = fopen(CONFIG_ROOT "/vpn/config", "r"))) {
                fprintf(stderr, "Couldn't open vpn settings file");
                exit(1);
        }
        while (fgets(s, STRING_SIZE, file) != NULL) {
                char *key;
                char *name;
                char *type;
                char *interface;
                if (!decode_line(s,&key,&name,&type,&interface))
                    continue;
                /* search interface */
                if (!enable_red && strcmp (interface, "RED") == 0) {
                        // when RED is up, find interface name in special file
                        FILE *ifacefile = NULL;
                        if ((ifacefile = fopen(CONFIG_ROOT "/red/iface", "r"))) {
                            if (fgets(if_red, STRING_SIZE, ifacefile)) {
                                if (if_red[strlen(if_red) - 1] == '\n')
                                        if_red[strlen(if_red) - 1] = '\0';
                            }
                            fclose (ifacefile);

                            if (VALID_DEVICE(if_red))
                                enable_red+=2;                  // present and running
                        }
                }

                if (!enable_green && strcmp (interface, "GREEN") == 0) {
                        enable_green = 1;
                        findkey(kv, "GREEN_DEV", if_green);
                        if (VALID_DEVICE(if_green))
                            enable_green++;
                        else
                            fprintf(stderr, "IPSec enabled on green but green interface is invalid or not found\n");
                }

                if (!enable_orange && strcmp (interface, "ORANGE") == 0) {
                        enable_orange = 1;
                        findkey(kv, "ORANGE_DEV", if_orange);
                        if (VALID_DEVICE(if_orange))
                            enable_orange++;
                        else
                            fprintf(stderr, "IPSec enabled on orange but orange interface is invalid or not found\n");
                }

                if (!enable_blue && strcmp (interface, "BLUE") == 0) {
                        enable_blue++;
                        findkey(kv, "BLUE_DEV", if_blue);
                        if (VALID_DEVICE(if_blue))
                            enable_blue++;
                        else
                            fprintf(stderr, "IPSec enabled on blue but blue interface is invalid or not found\n");

                }
        }
        fclose(file);
        freekeyvalues(kv);

        // do nothing if something is in error condition
        if ((enable_red==1) || (enable_green==1) || (enable_orange==1) || (enable_blue==1) )
            exit(1);

        // exit if nothing to do
        if ( (enable_red+enable_green+enable_orange+enable_blue) == 0 )
            exit(0);

        // open needed ports
        // todo: read a nat_t indicator to allow or not openning UDP/4500
        if (enable_red==2)
                open_physical(if_red, 4500);

        if (enable_green==2)
                open_physical(if_green, 4500);

        if (enable_orange==2)
                open_physical(if_orange, 4500);

        if (enable_blue==2)
                open_physical(if_blue, 4500);

        // start the system
        if ((argc == 2) && strcmp(argv[1], "S") == 0) {
                safe_system("/etc/rc.d/init.d/ipsec restart >/dev/null");
                safe_system("/usr/local/bin/vpn-watch &");
                exit(0);
        }

        // it is a selective start or stop
        // second param is only a number 'key'
        if ((argc == 2) || strspn(argv[2], NUMBERS) != strlen(argv[2])) {
                fprintf(stderr, "Bad arg\n");
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
                char *interface;
                if (!decode_line(s,&key,&name,&type,&interface))
                        continue;

                // start/stop a vpn if belonging to specified interface
                if (strcmp(argv[1], interface) == 0 ) {
                            if (strcmp(argv[2], "0")==0)
                                turn_connection_off (name);
                            else
                                turn_connection_on (name, type);
                        continue;
                }
                // is it the 'key' requested ?
                if (strcmp(argv[2], key) != 0)
                        continue;
                // Start or Delete this Connection
                if (strcmp(argv[1], "S") == 0)
                        turn_connection_on (name, type);
                else
                if (strcmp(argv[1], "D") == 0)
                        turn_connection_off (name);
                else {
                        fprintf(stderr, "Bad command\n");
                        exit(1);
                }
        }
        fclose(file);
        return 0;
}
