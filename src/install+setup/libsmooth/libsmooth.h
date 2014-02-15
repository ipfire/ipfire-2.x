/* SmoothWall libsmooth.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains prototypes for library functions.
 * 
 */

#ifndef ___LIBSMOOTH_H
#define ___LIBSMOOTH_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <wchar.h>
#include <locale.h>
#include <unistd.h>
#include <sys/file.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <newt.h>
#include <dirent.h>
#include <sys/mount.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <linux/cdrom.h>
#include <sys/ioctl.h>

#include "langs.h"

#define STRING_SIZE 1024

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

struct keyvalue
{
 	char key[STRING_SIZE];
 	char value[STRING_SIZE];
 	struct keyvalue *next;  
};
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


/* libsmooth.c */
void reboot(void);
void stripnl(char *s);
int mysystem(char *command);
void errorbox(char *message);
int statuswindowscroll(int width, int height, char *title, char *text, ...);
int disclaimerbox(char *message);
void statuswindow(int width, int height, char *title, char *text, ...);
int runcommandwithprogress(int width, int height, char *title, char *command,
	int lines, char *text, ...);
int runcommandwithstatus(char *command, char *message);
int runhiddencommandwithstatus(char *command, char *message);
int checkformodule(char *module); 
int replace(char filename1[], char *from, char *to);
char* get_version(void);
                                
/* netstuff.c */
int changeaddress(struct keyvalue *kv, char *colour, int typeflag,
	char *defaultdhcphostname);
int gettype(char *type);
int setnetaddress(struct keyvalue *kv, char *colour);
void networkdialogcallbacktype(newtComponent cm, void *data);
int interfacecheck(struct keyvalue *kv, char *colour);
int rename_nics(void);
int init_knics(void);
int create_udev(void);
int scan_network_cards(void);
int nicmenu(int colour);
int clear_card_entry(int cards);
int ask_clear_card_entry(int cards);
int manualdriver(char *driver, char *driveroptions);
	  
/* varval.c */
struct keyvalue *initkeyvalues(void);
void freekeyvalues(struct keyvalue *head);
int readkeyvalues(struct keyvalue *head, char *filename);
int writekeyvalues(struct keyvalue *head, char *filename);
int findkey(struct keyvalue *head, char *key, char *value);
void appendkeyvalue(struct keyvalue *head, char *key, char *value);
void replacekeyvalue(struct keyvalue *head, char *key, char *value);

#endif

