/* SmoothWall libsmooth.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains prototypes for library functions.
 * 
 * $Id: libsmooth.h,v 1.4.2.3 2005/10/30 23:25:35 franck78 Exp $
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

#define STRING_SIZE 1023

#define ADDRESS 0
#define NETADDRESS 1
#define NETMASK 2
#define DHCP 3
#define NETCHANGE_TOTAL 4

struct keyvalue
{
 	char key[STRING_SIZE];
 	char value[STRING_SIZE];
 	struct keyvalue *next;  
};

/* for stuff in net.c */
struct nic
{
	char *description;
	char *modulename;
};

/* libsmooth.c */
void reboot(void);
void stripnl(char *s);
int mysystem(char *command);
void errorbox(char *message);
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
int probecards(char *driver, char *driveroptions);
int choosecards(char *driver, char *driveroptions);
int manualdriver(char *driver, char *driveroptions);
int countcards(void);
int findnicdescription(char *modulename, char *description);
	  
/* data.c */
struct keyvalue *initkeyvalues(void);
void freekeyvalues(struct keyvalue *head);
int readkeyvalues(struct keyvalue *head, char *filename);
int writekeyvalues(struct keyvalue *head, char *filename);
int findkey(struct keyvalue *head, char *key, char *value);
void appendkeyvalue(struct keyvalue *head, char *key, char *value);
void replacekeyvalue(struct keyvalue *head, char *key, char *value);

#endif

