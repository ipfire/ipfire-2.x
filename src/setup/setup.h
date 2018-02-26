/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Main include file.
 * 
 * $Id: setup.h,v 1.4 2003/12/11 11:25:54 riddles Exp $
 * 
 */

#include <newt.h>
#include <libsmooth.h>

/* hostname.c */
int handlehostname(void);

/* domainname.c */
int handledomainname(void);

/* networking.c */
int handlenetworking(void);

/* dhcp.c */
int handledhcp(void);

/* passwords.c */
int handlerootpassword(void);
int handlesetuppassword(void);
int handleadminpassword(void);

/* misc.c */
int writehostsfiles(void);

/* keymap.c */
int handlekeymap(void);

/* timezone.c */
int handletimezone(void);

/* netstuff.c */
#define ADDRESS 0
#define NETADDRESS 1
#define NETMASK 2
#define DHCP 3
#define NETCHANGE_TOTAL 4

#define SCANNED_NICS "/var/ipfire/ethernet/scanned_nics"
#define SYSDIR "/sys/class/net"

#define _GREEN_CARD_ 0
#define _RED_CARD_ 1
#define _ORANGE_CARD_ 2
#define _BLUE_CARD_ 3

#define MAX_NICS 20

struct nic
{
	char driver[80];
	char description[256];
	char macaddr[20];
	char nic[20];
};

struct knic
{
	char driver[80];
	char description[256];
	char macaddr[20];
	char colour[20];
};

int changeaddress(struct keyvalue *kv, char *colour, int typeflag,
	char *defaultdhcphostname);
int gettype(char *type);
int setnetaddress(struct keyvalue *kv, char *colour);
void networkdialogcallbacktype(newtComponent cm, void *data);
int interfacecheck(struct keyvalue *kv, char *colour);
int rename_nics(void);
int init_knics(void);
int scan_network_cards(void);
int nicmenu(int colour);
int clear_card_entry(int cards);
int ask_clear_card_entry(int cards);
int manualdriver(char *driver, char *driveroptions);
